
import pytest

from rotkehlchen.accounting.structures.balance import Balance
from rotkehlchen.assets.asset import Asset, EvmToken
from rotkehlchen.chain.evm.constants import ZERO_ADDRESS
from rotkehlchen.chain.evm.decoding.aave.constants import CPT_AAVE_V3
from rotkehlchen.chain.evm.decoding.aave.v3.constants import POOL_ADDRESS
from rotkehlchen.chain.evm.decoding.constants import CPT_GAS
from rotkehlchen.chain.evm.decoding.safe.constants import CPT_SAFE_MULTISIG
from rotkehlchen.chain.evm.types import string_to_evm_address
from rotkehlchen.constants.assets import (
    A_ETH,
    A_OP,
    A_POLYGON_POS_MATIC,
    A_USDC,
    A_USDT,
    A_WBTC,
    A_WETH,
    A_XDAI,
)
from rotkehlchen.fval import FVal
from rotkehlchen.history.events.structures.evm_event import EvmEvent
from rotkehlchen.history.events.structures.types import HistoryEventSubType, HistoryEventType
from rotkehlchen.tests.unit.decoders.test_paraswap import A_POLYGON_POS_USDC
from rotkehlchen.tests.utils.constants import A_OPTIMISM_USDT
from rotkehlchen.tests.utils.ethereum import get_decoded_events_of_transaction
from rotkehlchen.types import Location, TimestampMS, deserialize_evm_tx_hash


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x93a208b0d7007f5733ea23F65bACF101Be8aC6cD']])
def test_aave_v3_enable_collateral(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x867d09a777ca7c5cbccd281d197ffbed327b5a8f07153483e94f75d4e1d04413')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711029839000)
    deposit_amount, gas_fees = '99503', '0.007154122119159412'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=183,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.DEPOSIT,
            event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
            asset=A_USDT,
            balance=Balance(amount=FVal(deposit_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Deposit {deposit_amount} USDT into AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a'),
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=184,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=EvmToken('eip155:1/erc20:0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a'),
            balance=Balance(amount=FVal(deposit_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Receive {deposit_amount} aEthUSDT from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=186,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_USDT,
            balance=Balance(),
            location_label=ethereum_accounts[0],
            notes='Enable USDT as collateral on AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x203b2E862C57fbAc813c05c46B6e1242844724A2']])
def test_aave_v3_disable_collateral(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x1f7614ba2425f3345d02bf1518c81ab3aa46e888553b409f3c9a360259bc7988')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711028735000)
    returned_amount, withdraw_amount, gas_fees = '0.3', '0.30005421', '0.005234272941346752'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=261,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_WBTC,
            balance=Balance(),
            location_label=ethereum_accounts[0],
            notes='Disable WBTC as collateral on AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=262,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=EvmToken('eip155:1/erc20:0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8'),
            balance=Balance(amount=FVal(returned_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Return {returned_amount} aEthWBTC to AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=263,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=A_WBTC,
            balance=Balance(amount=FVal(withdraw_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Withdraw {withdraw_amount} WBTC from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x08c14B32C8A48894E4b933090EBcC9CE33B21135']])
def test_aave_v3_deposit(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x062bb6b01d4ac5fabd7b7783965d22589d289e44bb0227bb2fc0adaad7eb563b')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711030499000)
    deposit_amount, gas_fees = '71657.177259074315114745', '0.009902467860617334'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=219,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.DEPOSIT,
            event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
            asset=EvmToken('eip155:1/erc20:0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32'),  # LDO
            balance=Balance(amount=FVal(deposit_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Deposit {deposit_amount} LDO into AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x9A44fd41566876A39655f74971a3A6eA0a17a454'),
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=220,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=EvmToken('eip155:1/erc20:0x9A44fd41566876A39655f74971a3A6eA0a17a454'),  # aWETH
            balance=Balance(amount=FVal(deposit_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Receive {deposit_amount} aEthLDO from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0xabE9e5d199E1E411098181b6a5Ab9f5f65d91389']])
def test_aave_v3_withdraw(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0xf184c285dab9ea6c72d18025c65202e3d9e5ec3181209a6cbedf88dfd4c8283f')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711030631000)
    return_amount, withdraw_amount, gas_fees = '6770.796829', '6779.85', '0.00692900756596481'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=1,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=EvmToken('eip155:1/erc20:0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a'),
            balance=Balance(amount=FVal(return_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Return {return_amount} aEthUSDT to AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=2,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=A_USDT,
            balance=Balance(amount=FVal(withdraw_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Withdraw {withdraw_amount} USDT from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x08c14B32C8A48894E4b933090EBcC9CE33B21135']])
def test_aave_v3_borrow(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x44367976e841cde459d84aec984d5fae4466b2978b1d71c9cd916bb79792ee20')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711030571000)
    borrowed_amount, gas_fees = '79931.500229', '0.011111128567338506'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=217,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=EvmToken('eip155:1/erc20:0x72E95b8931767C79bA4EeE721354d6E99a61D004'),
            balance=Balance(amount=FVal(borrowed_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Receive {borrowed_amount} variableDebtEthUSDC from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=221,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.GENERATE_DEBT,
            asset=A_USDC,
            balance=Balance(amount=FVal(borrowed_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Borrow {borrowed_amount} USDC from AAVE v3 with variable APY 13.24%',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x9CBF099ff424979439dFBa03F00B5961784c06ce']])
def test_aave_v3_repay(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x440dddaad9f8d9c6d99777494640520854cca8dd102fb557f1654f5746da5f7e')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711030643000)
    return_amount, repay_amount, gas_fees = '123942.602894', '123961.452987', '0.00646693553105336'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=158,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=EvmToken('eip155:1/erc20:0x72E95b8931767C79bA4EeE721354d6E99a61D004'),
            balance=Balance(amount=FVal(return_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Return {return_amount} variableDebtEthUSDC to AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=161,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.PAYBACK_DEBT,
            asset=A_USDC,
            balance=Balance(amount=FVal(repay_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Repay {repay_amount} USDC on AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x7420fA58bA44E1141d5E9ADB6903BE549f7cE0b5']])
def test_aave_v3_liquidation(database, ethereum_inquirer, ethereum_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0xc1a03e87f1c0446ddd5a77f7eb906831c72618a921a1f6f9f430f612edca0531')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1692320627000)
    payback_amount, liquidation_amount, fee_amount = '23.378156', '0.01887243880551005', '0.000090391508992915'  # noqa: E501
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=242,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_WETH,
            balance=Balance(),
            location_label=ethereum_accounts[0],
            notes='Disable WETH as collateral on AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=243,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.PAYBACK_DEBT,
            asset=EvmToken('eip155:1/erc20:0x72E95b8931767C79bA4EeE721354d6E99a61D004'),
            balance=Balance(amount=FVal(payback_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Payback {payback_amount} variableDebtEthUSDC for an AAVE v3 position',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
            extra_data={'is_liquidation': True},
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=247,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.LIQUIDATE,
            asset=EvmToken('eip155:1/erc20:0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8'),
            balance=Balance(amount=FVal(liquidation_amount)),
            location_label=ethereum_accounts[0],
            notes=f'An AAVE v3 position got liquidated for {liquidation_amount} aEthWETH',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'),
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=252,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=EvmToken('eip155:1/erc20:0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8'),
            balance=Balance(amount=FVal(fee_amount)),
            location_label=ethereum_accounts[0],
            notes=f'Spend {fee_amount} aEthWETH as an AAVE v3 fee',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('polygon_pos_accounts', [['0xA55EaD17fa903b1218dc6a79c47b54C9370E20AB']])
def test_aave_v3_enable_collateral_polygon(database, polygon_pos_inquirer, polygon_pos_accounts) -> None:  # noqa: E501
    tx_hash = deserialize_evm_tx_hash('0x8002f1a3044bcdec645d512713724f09551c18a14c67509417c83961b230294b')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=polygon_pos_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711448176000)
    deposit_amount, gas_fees = '1245.829008', '0.010974492076211867'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.POLYGON_POS,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_POLYGON_POS_MATIC,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=polygon_pos_accounts[0],
            notes=f'Burned {gas_fees} MATIC for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=571,
            timestamp=timestamp,
            location=Location.POLYGON_POS,
            event_type=HistoryEventType.DEPOSIT,
            event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
            asset=A_POLYGON_POS_USDC,
            balance=Balance(amount=FVal(deposit_amount)),
            location_label=polygon_pos_accounts[0],
            notes=f'Deposit {deposit_amount} USDC into AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0xA4D94019934D8333Ef880ABFFbF2FDd611C762BD'),
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=572,
            timestamp=timestamp,
            location=Location.POLYGON_POS,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=Asset('eip155:137/erc20:0xA4D94019934D8333Ef880ABFFbF2FDd611C762BD'),
            balance=Balance(amount=FVal(deposit_amount)),
            location_label=polygon_pos_accounts[0],
            notes=f'Receive {deposit_amount} aPolUSDCn from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=574,
            timestamp=timestamp,
            location=Location.POLYGON_POS,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_POLYGON_POS_USDC,
            balance=Balance(),
            location_label=polygon_pos_accounts[0],
            notes='Enable USDC as collateral on AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=POOL_ADDRESS,
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('arbitrum_one_accounts', [['0x645C22593c232Ae78a7eCbaC93b38cbaC535ef12']])
def test_aave_v3_withdraw_arbitrum_one(database, arbitrum_one_inquirer, arbitrum_one_accounts) -> None:  # noqa: E501
    tx_hash = deserialize_evm_tx_hash('0x09d5e6da511fb88e8a7db6f1209542610a9d3873048e405b88c7a766d7210d6f')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=arbitrum_one_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711450245000)
    return_amount, withdraw_amount, gas_fees = '11.905748099167569087', '12', '0.00000490517'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ARBITRUM_ONE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=arbitrum_one_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=1,
            timestamp=timestamp,
            location=Location.ARBITRUM_ONE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=Asset('eip155:42161/erc20:0x191c10Aa4AF7C30e871E70C95dB0E4eb77237530'),
            balance=Balance(amount=FVal(return_amount)),
            location_label=arbitrum_one_accounts[0],
            notes=f'Return {return_amount} aArbLINK to AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=2,
            timestamp=timestamp,
            location=Location.ARBITRUM_ONE,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=Asset('eip155:42161/erc20:0xf97f4df75117a78c1A5a0DBb814Af92458539FB4'),
            balance=Balance(amount=FVal(withdraw_amount)),
            location_label=arbitrum_one_accounts[0],
            notes=f'Withdraw {withdraw_amount} LINK from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x191c10Aa4AF7C30e871E70C95dB0E4eb77237530'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('base_accounts', [['0xaafc3e3C8B4fD93584256E6D49a9C364648E66cE']])
def test_aave_v3_borrow_base(database, base_inquirer, base_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x92b6fef0623a3f56daa651968819f2e5b7a982037c19fed2166e4c00ba4d6350')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=base_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711452273000)
    borrowed_amount, gas_fees = '0.181', '0.000090985761072991'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=base_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=178,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=EvmToken('eip155:8453/erc20:0x41A7C3f5904ad176dACbb1D99101F59ef0811DC1'),
            balance=Balance(amount=FVal(borrowed_amount)),
            location_label=base_accounts[0],
            notes=f'Receive {borrowed_amount} variableDebtBaswstETH from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=181,
            timestamp=timestamp,
            location=Location.BASE,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.GENERATE_DEBT,
            asset=EvmToken('eip155:8453/erc20:0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452'),
            balance=Balance(amount=FVal(borrowed_amount)),
            location_label=base_accounts[0],
            notes=f'Borrow {borrowed_amount} wstETH from AAVE v3 with variable APY 0.30%',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x99CBC45ea5bb7eF3a5BC08FB1B7E56bB2442Ef0D'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('gnosis_accounts', [['0x91ed7A7fd3072885c1ec905C932717Df6A8aE2cA']])
def test_aave_v3_withdraw_gnosis(database, gnosis_inquirer, gnosis_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x1f3cae37be928563d154c534c98f41eefe9201eb3d0129c99c1ecb51f83e5596')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=gnosis_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711453785000)
    withdraw_amount, gas_fees = '4300', '0.000876816'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.GNOSIS,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_XDAI,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=gnosis_accounts[0],
            notes=f'Burned {gas_fees} XDAI for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=1,
            timestamp=timestamp,
            location=Location.GNOSIS,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=EvmToken('eip155:100/erc20:0x7a5c3860a77a8DC1b225BD46d0fb2ac1C6D191BC'),
            balance=Balance(amount=FVal(withdraw_amount)),
            location_label=gnosis_accounts[0],
            notes=f'Return {withdraw_amount} aGnosDAI to AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=2,
            timestamp=timestamp,
            location=Location.GNOSIS,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=EvmToken('eip155:100/erc20:0xaf204776c7245bF4147c2612BF6e5972Ee483701'),
            balance=Balance(amount=FVal(withdraw_amount)),
            location_label=gnosis_accounts[0],
            notes=f'Withdraw {withdraw_amount} sDAI from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x7a5c3860a77a8DC1b225BD46d0fb2ac1C6D191BC'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('optimism_accounts', [['0xdbD5D31B7f48adC13A0aB0c591F7e3D4f9642e69']])
def test_aave_v3_borrow_optimism(database, optimism_inquirer, optimism_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0xb043a7f28cccd6cb0392db47cea4607f8cf3b91b6510669a0a62588b66eb7fcf')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=optimism_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711455941000)
    borrowed_amount, gas_fees = '2000', '0.000018093759776472'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.OPTIMISM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=optimism_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=7,
            timestamp=timestamp,
            location=Location.OPTIMISM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=EvmToken('eip155:10/erc20:0xfb00AC187a8Eb5AFAE4eACE434F493Eb62672df7'),
            balance=Balance(amount=FVal(borrowed_amount)),
            location_label=optimism_accounts[0],
            notes=f'Receive {borrowed_amount} variableDebtOptUSDT from AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=10,
            timestamp=timestamp,
            location=Location.OPTIMISM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.GENERATE_DEBT,
            asset=A_OPTIMISM_USDT,
            balance=Balance(amount=FVal(borrowed_amount)),
            location_label=optimism_accounts[0],
            notes=f'Borrow {borrowed_amount} USDT from AAVE v3 with variable APY 13.71%',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x6ab707Aca953eDAeFBc4fD23bA73294241490620'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('scroll_accounts', [['0x3E6B4598E5bfeEc911f344E546C9EbFe4A00d770']])
def test_aave_v3_repay_scroll(database, scroll_inquirer, scroll_accounts) -> None:
    tx_hash = deserialize_evm_tx_hash('0x66010f353be60adaa004f839d37cecd22c35c580060eeaffb9a28ebe169e1692')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=scroll_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp = TimestampMS(1711456958000)
    return_amount, repay_amount, gas_fees = '14459.999417', '14460.008663', '0.000386215421959661'
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.SCROLL,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=scroll_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=66,
            timestamp=timestamp,
            location=Location.SCROLL,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=EvmToken('eip155:534352/erc20:0x3d2E209af5BFa79297C88D6b57F89d792F6E28EE'),
            balance=Balance(amount=FVal(return_amount)),
            location_label=scroll_accounts[0],
            notes=f'Return {return_amount} variableDebtScrUSDC to AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=ZERO_ADDRESS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=69,
            timestamp=timestamp,
            location=Location.SCROLL,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.PAYBACK_DEBT,
            asset=EvmToken('eip155:534352/erc20:0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4'),
            balance=Balance(amount=FVal(repay_amount)),
            location_label=scroll_accounts[0],
            notes=f'Repay {repay_amount} USDC on AAVE v3',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x1D738a3436A8C49CefFbaB7fbF04B660fb528CbD'),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr()
@pytest.mark.parametrize('ethereum_accounts', [['0x35E0091D67B5e213db857F605c2047cA29A8800d']])
def test_non_aave_tx(database, ethereum_inquirer, ethereum_accounts) -> None:
    """Test that the non-aave transactions happened through flash loans are not decoded
    as aave events."""
    tx_hash = deserialize_evm_tx_hash('0xf5b4c6f3b4e5bce1f91f7e7eab6185b6d1518e63dea637c79d7f1bbb97edda67')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=ethereum_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp, multisig, gas_fees = TimestampMS(1713496487000), '0x35542F2c7D18716401A38cc7f08Bf5Bf61f371cc', '0.018530645755598298'  # noqa: E501
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas_fees)),
            location_label=ethereum_accounts[0],
            notes=f'Burned {gas_fees} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=1,
            timestamp=timestamp,
            location=Location.ETHEREUM,
            event_type=HistoryEventType.INFORMATIONAL,
            event_subtype=HistoryEventSubType.NONE,
            asset=A_ETH,
            balance=Balance(),
            location_label=ethereum_accounts[0],
            notes=f'Successfully executed safe transaction 0x69e95bb0e8452641e165a7cf2f2fa83afb5dc6a6a576bd6e0bc36094df5cc27c for multisig {multisig}',  # noqa: E501
            counterparty=CPT_SAFE_MULTISIG,
            address=string_to_evm_address(multisig),
        ),
    ]
    assert events == expected_events


@pytest.mark.vcr(filter_query_parameters=['apikey'])
@pytest.mark.parametrize('optimism_accounts', [['0x9531C059098e3d194fF87FebB587aB07B30B1306']])
def test_claim_incentives_reward(database, optimism_inquirer, optimism_accounts) -> None:
    """Test that claim rewards for incentives works"""
    tx_hash = deserialize_evm_tx_hash('0xa2860ca34ea7558240c44f3d0895a9cf832bd0dd952b2b27d3ae34ba6d45697c')  # noqa: E501
    events, _ = get_decoded_events_of_transaction(
        evm_inquirer=optimism_inquirer,
        database=database,
        tx_hash=tx_hash,
    )
    timestamp, gas, user, amount = TimestampMS(1666883965000), '0.000198192753532852', optimism_accounts[0], '558.228460248737908186'  # noqa: E501
    expected_events = [
        EvmEvent(
            tx_hash=tx_hash,
            sequence_index=0,
            timestamp=timestamp,
            location=Location.OPTIMISM,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal(gas)),
            location_label=user,
            notes=f'Burned {gas} ETH for gas',
            counterparty=CPT_GAS,
        ), EvmEvent(
            tx_hash=tx_hash,
            sequence_index=15,
            timestamp=timestamp,
            location=Location.OPTIMISM,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.REWARD,
            asset=A_OP,
            balance=Balance(amount=FVal(amount)),
            location_label=user,
            notes=f'Claim {amount} OP from Aave incentives',
            counterparty=CPT_AAVE_V3,
            address=string_to_evm_address('0x2501c477D0A35545a387Aa4A3EEe4292A9a8B3F0'),
        ),
    ]
    assert events == expected_events
