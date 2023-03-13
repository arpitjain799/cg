from cg.cli.add import add
from cg.constants import EXIT_SUCCESS
from cg.models.cg_config import CGConfig
from cg.store import Store
from click.testing import CliRunner


def test_add_user(cli_runner: CliRunner, base_context: CGConfig):
    # GIVEN a database with a customer in it that we can connect the user to
    disk_store: Store = base_context.status_db
    customer_id = "custtest"
    customer = disk_store.add_customer(
        internal_id=customer_id,
        name="Test Customer",
        scout_access=False,
        invoice_address="Street nr, 12345 Uppsala",
        invoice_reference="ABCDEF",
    )
    disk_store.add_commit(customer)
    # GIVEN that there is a certain number of users
    nr_users = disk_store.User.query.count()

    # WHEN adding a new user
    name, email = "Paul T. Anderson", "paul.anderson@magnolia.com"
    result = cli_runner.invoke(add, ["user", "-c", customer_id, email, name], obj=base_context)

    # THEN exit successfully
    assert result.exit_code == EXIT_SUCCESS
    assert disk_store.User.query.count() == nr_users + 1
