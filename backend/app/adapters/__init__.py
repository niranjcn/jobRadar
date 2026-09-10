from app.adapters.amazon import AmazonAdapter
from app.adapters.ashby import AshbyAdapter
from app.adapters.avature import AvatureAdapter
from app.adapters.base import JobSourceAdapter
from app.adapters.custom import CustomAdapter
from app.adapters.emirates import EmiratesAdapter
from app.adapters.google import GoogleAdapter
from app.adapters.greenhouse import GreenhouseAdapter
from app.adapters.icims import IcimsAdapter
from app.adapters.lever import LeverAdapter
from app.adapters.oracle import OracleAdapter
from app.adapters.phenom import PhenomAdapter
from app.adapters.remotive import RemotiveAdapter
from app.adapters.successfactors import SuccessFactorsAdapter
from app.adapters.weworkremotely import WeworkremotelyAdapter
from app.adapters.workday import WorkdayAdapter


def adapter_for(ats_type: str) -> JobSourceAdapter:
    if ats_type == GreenhouseAdapter.ats_type:
        return GreenhouseAdapter()
    if ats_type == LeverAdapter.ats_type:
        return LeverAdapter()
    if ats_type == AshbyAdapter.ats_type:
        return AshbyAdapter()
    if ats_type == WorkdayAdapter.ats_type:
        return WorkdayAdapter()
    if ats_type == OracleAdapter.ats_type:
        return OracleAdapter()
    if ats_type == IcimsAdapter.ats_type:
        return IcimsAdapter()
    if ats_type == SuccessFactorsAdapter.ats_type:
        return SuccessFactorsAdapter()
    if ats_type == PhenomAdapter.ats_type:
        return PhenomAdapter()
    if ats_type == AvatureAdapter.ats_type:
        return AvatureAdapter()
    if ats_type == AmazonAdapter.ats_type:
        return AmazonAdapter()
    if ats_type == GoogleAdapter.ats_type:
        return GoogleAdapter()
    if ats_type == RemotiveAdapter.ats_type:
        return RemotiveAdapter()
    if ats_type == WeworkremotelyAdapter.ats_type:
        return WeworkremotelyAdapter()
    if ats_type == CustomAdapter.ats_type:
        return CustomAdapter()
    if ats_type == EmiratesAdapter.ats_type:
        return EmiratesAdapter()
    raise ValueError(f"no adapter registered for ats_type={ats_type!r}")
