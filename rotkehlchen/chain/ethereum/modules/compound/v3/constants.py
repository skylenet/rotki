from typing import Final
from rotkehlchen.chain.evm.types import string_to_evm_address

CPT_COMPOUND_V3: Final = 'compound-v3'
COMPOUND_REWARDS_ADDRESS: Final = string_to_evm_address('0x1B0e765F6224C21223AeA2af16c1C46E38885a40')  # noqa: E501
COMPOUND_V3_SUPPLY_COLLATERAL: Final = b'\xfaV\xf7\xb2O\x17\x18=\x81\x89M:\xc2\xeeeN<&8\x8d\x17\xa2\x8d\xbd\x95I\xb8\x11C\x04\xe1\xf4'  # noqa: E501
COMPOUND_V3_SUPPLY: Final = b'\xd1\xcf=\x15m_\x8f\rP\xf6\xc1"\xed`\x9c\xec\t\xd3\\\x9b\x9f\xb3\xff\xf6\xea\tY\x13M\xaeBN'  # noqa: E501
COMPOUND_V3_WITHDRAW_COLLATERAL: Final = b'\xd6\xd4\x80\xd5\xb3\x06\x8d\xb0\x03S;\x17\rgV\x14\x94\xd7.;\xf9\xfa@\xa2fG\x13Q\xeb\xba\x9e\x16'  # noqa: E501
COMPOUND_V3_WITHDRAW: Final = b'\x9b\x1b\xfa\x7f\xa9\xeeB\n\x16\xe1$\xf7\x94\xc3Z\xc9\xf9\x04r\xac\xc9\x91@\xeb/dG\xc7\x14\xca\xd8\xeb'  # noqa: E501
