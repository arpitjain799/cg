from typing import Dict, List

from cg.exc import OrderError
from cg.meta.orders.rml_order_form import Orderform, OrderSample, Pool


def get_pools(orderform: Orderform) -> List[Pool]:
    """create pools from samples in orderform

    Check that all samples from one pool has the same application
    """
    pools: Dict[str, Pool] = {}
    sample: OrderSample
    for sample in orderform.samples:
        pool_name = sample.pool
        application = sample.application
        if pool_name not in pools:
            pools[pool_name] = Pool(
                name=pool_name,
                data_analysis=sample.data_analysis,
                data_delivery=sample.data_delivery,
                application=application,
            )
            continue
        # each pool must only have one application type
        if pools[pool_name].application != application:
            raise OrderError(
                f"different application in pool: {pool_name} - {[pools[pool_name].application, application]}"
            )

    return [pools[pool_name] for pool_name in pools]
