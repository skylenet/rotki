<script setup lang="ts">
import { Blockchain } from '@rotki/common/lib/blockchain';
import {
  AIRDROP_POAP,
  type Airdrop,
  type AirdropDetail,
  Airdrops,
  type PoapDelivery,
} from '@/types/defi/airdrops';
import { TaskType } from '@/types/task-type';
import AirdropDisplay from '@/components/defi/airdrops/AirdropDisplay.vue';
import type { AddressData, BlockchainAccount } from '@/types/blockchain/accounts';
import type { DataTableColumn, TablePaginationData } from '@rotki/ui-library-compat';
import type { TaskMeta } from '@/types/task';

type Statuses = '' | 'unknown' | 'unclaimed' | 'claimed';
const ETH = Blockchain.ETH;
const { t } = useI18n();
const { awaitTask } = useTaskStore();
const { notify } = useNotificationsStore();
const { fetchAirdrops: fetchAirdropsCaller } = useDefiApi();
const hideUnknownAlert = useLocalStorage('rotki.airdrops.hide_unknown_alert', false);

const airdrops = ref<Airdrops>({});
const expanded = ref<Airdrop[]>([]);
const loading = ref<boolean>(false);
const status = ref<Statuses>('');
const pagination = ref<TablePaginationData>();
const selectedAccounts = ref<BlockchainAccount<AddressData>[]>([]);
const statusFilters = ref<{ text: string; value: Statuses }[]>([
  { text: t('common.all'), value: '' },
  { text: t('common.unknown'), value: 'unknown' },
  { text: t('common.unclaimed'), value: 'unclaimed' },
  { text: t('common.claimed'), value: 'claimed' },
]);

const refreshTooltip = computed<string>(() => t('helpers.refresh_header.tooltip', {
  title: t('airdrops.title').toLocaleLowerCase(),
}));

const airdropAddresses = computed<string[]>(() => Object.keys(get(airdrops)));

const rows = computed<(Airdrop & { index: number })[]>(() => {
  const addresses = get(selectedAccounts).map(account => getAccountAddress(account));
  const data = filterByAddress(get(airdrops), addresses);
  return data.filter((airdrop) => {
    const currentStatus = get(status);
    switch (currentStatus) {
      case 'unknown':
        return !airdrop.hasDecoder;
      case 'unclaimed':
        return airdrop.hasDecoder && !airdrop.claimed;
      case 'claimed':
        return airdrop.claimed;
      default:
        return true;
    }
  }).map((value, index) => ({
    ...value,
    index,
  }));
});

const cols = computed<DataTableColumn[]>(() => [
  {
    label: t('airdrops.headers.source'),
    key: 'source',
    width: '200px',
  },
  {
    label: t('common.address'),
    key: 'address',
  },
  {
    label: t('common.amount'),
    key: 'amount',
    align: 'end',
  },
  {
    label: t('common.status'),
    key: 'claimed',
  },
]);

function filterByAddress(data: Airdrops, addresses: string[]): Airdrop[] {
  const result: Airdrop[] = [];
  for (const address in data) {
    if (addresses.length > 0 && !addresses.includes(address))
      continue;

    const airdrop = data[address];
    for (const source in airdrop) {
      const element = airdrop[source];
      if (source === AIRDROP_POAP) {
        const details = element as PoapDelivery[];
        result.push({
          address,
          source,
          details: details.map(({ link, name, event }) => ({
            amount: bigNumberify('1'),
            link,
            name,
            event,
            claimed: false,
          })),
        });
      }
      else {
        const { amount, asset, link, claimed, hasDecoder } = element as AirdropDetail;
        result.push({
          address,
          amount,
          link,
          source,
          asset,
          claimed,
          hasDecoder,
        });
      }
    }
  }
  return result;
}

async function fetchAirdrops() {
  set(loading, true);
  try {
    const { taskId } = await fetchAirdropsCaller();
    const { result } = await awaitTask<Airdrops, TaskMeta>(
      taskId,
      TaskType.DEFI_AIRDROPS,
      {
        title: t('actions.defi.airdrops.task.title'),
      },
    );
    set(airdrops, Airdrops.parse(result));
  }
  catch (error: any) {
    if (!isTaskCancelled(error)) {
      logger.error(error);
      notify({
        title: t('actions.defi.airdrops.error.title'),
        message: t('actions.defi.airdrops.error.description', {
          error: error.message,
        }),
        display: true,
      });
    }
  }
  finally {
    set(loading, false);
  }
}

const hasDetails = (source: string): boolean => [AIRDROP_POAP].includes(source);

function expand(item: Airdrop) {
  set(expanded, get(expanded).includes(item) ? [] : [item]);
}

onMounted(async () => {
  await fetchAirdrops();
});

watch([status, selectedAccounts], () => {
  set(pagination, { ...get(pagination), page: 1 });
});
</script>

<template>
  <TablePageLayout
    :title="[
      t('navigation_menu.defi'),
      t('navigation_menu.defi_sub.airdrops'),
    ]"
  >
    <template #buttons>
      <RuiTooltip :open-delay="400">
        <template #activator>
          <RuiButton
            variant="outlined"
            color="primary"
            :loading="loading"
            @click="fetchAirdrops()"
          >
            <template #prepend>
              <RuiIcon name="refresh-line" />
            </template>
            {{ t('common.refresh') }}
          </RuiButton>
        </template>
        {{ refreshTooltip }}
      </RuiTooltip>
    </template>

    <RuiCard>
      <div class="flex flex-col md:flex-row flex-wrap items-start gap-4 mb-4">
        <BlockchainAccountSelector
          v-model="selectedAccounts"
          class="w-full flex-1 !shadow-none !border-none !p-0"
          no-padding
          dense
          outlined
          :chains="[ETH]"
          :usable-addresses="airdropAddresses"
        />
        <RuiMenuSelect
          v-model="status"
          :options="statusFilters"
          class="w-full flex-1"
          key-attr="value"
          text-attr="text"
          dense
          hide-details
          variant="outlined"
        />
      </div>

      <RuiAlert
        v-if="!hideUnknownAlert && status === 'unknown'"
        type="info"
        class="mb-4"
        closeable
        @close="hideUnknownAlert = true"
      >
        {{ t('airdrops.unknown_info') }}
      </RuiAlert>

      <RuiDataTable
        outlined
        :rows="rows"
        :cols="cols"
        :loading="loading"
        :pagination.sync="pagination"
        single-expand
        :expanded.sync="expanded"
        row-attr="index"
      >
        <template #item.address="{ row }">
          <HashLink :text="row.address" />
        </template>
        <template #item.amount="{ row }">
          <AmountDisplay
            v-if="!hasDetails(row.source)"
            :value="row.amount"
            :asset="row.asset"
          />
          <span v-else>{{ row.details.length }}</span>
        </template>
        <template #item.claimed="{ row: { claimed, hasDecoder } }">
          <RuiTooltip
            v-if="!hasDecoder"
            :popper="{ placement: 'top' }"
            :open-delay="400"
            tooltip-class="max-w-[12rem]"
          >
            <template #activator>
              <RuiChip
                color="info"
                size="sm"
              >
                {{ t('common.unknown') }}
              </RuiChip>
            </template>

            {{ t('airdrops.unknown_tooltip') }}
          </RuiTooltip>
          <RuiChip
            v-else
            :color="claimed ? 'success' : 'grey'"
            size="sm"
          >
            {{ claimed ? t('common.claimed') : t('common.unclaimed') }}
          </RuiChip>
        </template>
        <template #item.source="{ row }">
          <AirdropDisplay
            :source="row.source"
            :icon-url="row.iconUrl"
          />
        </template>
        <template #item.expand="{ row }">
          <ExternalLink
            v-if="!hasDetails(row.source)"
            :url="row.link"
            custom
          >
            <RuiButton
              variant="text"
              color="primary"
              icon
            >
              <RuiIcon
                size="16"
                name="external-link-line"
              />
            </RuiButton>
          </ExternalLink>
          <RuiTableRowExpander
            v-else
            :expanded="expanded.includes(row)"
            @click="expand(row)"
          />
        </template>
        <template #expanded-item="{ row }">
          <PoapDeliveryAirdrops
            v-if="hasDetails(row.source)"
            :items="row.details"
          />
        </template>
      </RuiDataTable>
    </RuiCard>
  </TablePageLayout>
</template>
