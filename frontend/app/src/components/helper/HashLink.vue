<script setup lang="ts">
import { Blockchain } from '@rotki/common/lib/blockchain';
import { truncateAddress } from '@/utils/truncate';
import {
  type ExplorerUrls,
  explorerUrls,
  isChains,
} from '@/types/asset/asset-urls';

const props = withDefaults(
  defineProps<{
    showIcon?: boolean;
    text?: string;
    fullAddress?: boolean;
    linkOnly?: boolean;
    noLink?: boolean;
    baseUrl?: string;
    chain?: string;
    evmChain?: string;
    buttons?: boolean;
    size?: number | string;
    truncateLength?: number;
    type?: keyof ExplorerUrls;
    disableScramble?: boolean;
    hideAliasName?: boolean;
    location?: string;
  }>(),
  {
    showIcon: true,
    text: '',
    fullAddress: false,
    linkOnly: false,
    noLink: false,
    baseUrl: undefined,
    chain: Blockchain.ETH,
    evmChain: undefined,
    buttons: false,
    size: 12,
    truncateLength: 4,
    type: 'address',
    disableScramble: false,
    hideAliasName: false,
    location: undefined,
  },
);
const { t } = useI18n();
const { copy } = useClipboard();

const { text, baseUrl, chain, evmChain, type, disableScramble, hideAliasName, location } = toRefs(props);
const { scrambleData, shouldShowAmount, scrambleHex, scrambleIdentifier } = useScramble();

const { explorers } = storeToRefs(useFrontendSettingsStore());
const { getChain, getChainInfoByName } = useSupportedChains();

const { addressNameSelector } = useAddressesNamesStore();
const addressName = computed(() => {
  const name = get(location);
  if (name && !get(getChainInfoByName(name)))
    return null;

  return get(addressNameSelector(text, chain));
});

const blockchain = computed(() => {
  if (isDefined(evmChain))
    return getChain(get(evmChain));

  return get(chain);
});

const aliasName = computed<string | null>(() => {
  if (get(hideAliasName) || get(scrambleData) || get(type) !== 'address')
    return null;

  const name = get(addressName);
  if (!name)
    return null;

  return name;
});

const truncatedAliasName = computed<string | null>(() => {
  const alias = get(aliasName);

  if (!alias)
    return alias;

  return truncateAddress(alias, 10);
});

const displayText = computed<string>(() => {
  const linkText = get(text);
  const linkType = get(type);

  if (get(disableScramble))
    return linkText;

  if (linkType === 'block' || consistOfNumbers(linkText))
    return scrambleIdentifier(linkText);

  return scrambleHex(linkText);
});

const base = computed<string>(() => {
  if (isDefined(baseUrl))
    return get(baseUrl);

  const selectedChain = get(blockchain);
  let base: string | undefined;
  if (isChains(selectedChain)) {
    const defaultExplorer: ExplorerUrls = explorerUrls[selectedChain];
    const linkType = get(type);

    const explorerSetting = get(explorers)[selectedChain];

    if (explorerSetting || defaultExplorer)
      base = explorerSetting?.[linkType] ?? defaultExplorer[linkType];
  }

  if (!base)
    return '';

  return base.endsWith('/') ? base : `${base}/`;
});

const url = computed<string>(() => get(base) + get(text));

const displayUrl = computed<string>(
  () => get(base) + truncateAddress(get(text), 10),
);

const { href, onLinkClick } = useLinks(url);
</script>

<template>
  <div class="flex flex-row shrink items-center gap-1">
    <template v-if="showIcon && !linkOnly && type === 'address'">
      <EnsAvatar
        :address="displayText"
        avatar
        size="22px"
      />
    </template>

    <template v-if="!linkOnly && !buttons">
      <span
        v-if="fullAddress"
        :class="{ blur: !shouldShowAmount }"
      >
        {{ displayText }}
      </span>

      <RuiTooltip
        v-else
        :popper="{ placement: 'top' }"
        :open-delay="400"
      >
        <template #activator>
          <span :class="{ blur: !shouldShowAmount }">
            <template v-if="truncatedAliasName">{{ truncatedAliasName }}</template>
            <template v-else>
              {{ truncateAddress(displayText, truncateLength) }}
            </template>
          </span>
        </template>
        <div
          v-if="aliasName && aliasName !== truncatedAliasName"
          class="font-bold"
        >
          {{ aliasName }}
        </div>
        {{ displayText }}
      </RuiTooltip>
    </template>

    <div class="flex items-center gap-1 pl-1">
      <RuiTooltip
        v-if="!linkOnly || buttons"
        :popper="{ placement: 'top' }"
        :open-delay="600"
      >
        <template #activator>
          <RuiButton
            variant="text"
            icon
            class="!bg-rui-grey-200 dark:!bg-rui-grey-900 hover:!bg-rui-grey-100 hover:dark:!bg-rui-grey-800"
            size="sm"
            color="primary"
            @click="copy(text)"
          >
            <RuiIcon
              name="file-copy-line"
              :size="size"
            />
          </RuiButton>
        </template>

        {{ t('common.actions.copy_to_clipboard') }}
      </RuiTooltip>

      <RuiTooltip
        v-if="linkOnly || !noLink || buttons"
        :popper="{ placement: 'top' }"
        :open-delay="600"
      >
        <template #activator>
          <RuiButton
            v-if="!!base"
            tag="a"
            icon
            variant="text"
            class="!bg-rui-grey-200 dark:!bg-rui-grey-900 hover:!bg-rui-grey-100 hover:dark:!bg-rui-grey-800"
            size="sm"
            color="primary"
            :href="href"
            target="_blank"
            @click="onLinkClick()"
          >
            <RuiIcon
              name="external-link-line"
              :size="size"
            />
          </RuiButton>
        </template>

        {{ t('hash_link.open_link') }}:
        {{ displayUrl }}
      </RuiTooltip>
    </div>
  </div>
</template>
