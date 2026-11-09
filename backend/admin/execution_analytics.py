from collections import Counter, defaultdict

from database.repos import get_all_executions, get_invitations


def get_analytics() -> dict:
    """
    Retrieve execution and invitation records and calculate
    administrative analytics.
    """

    executions = get_all_executions()
    invitations = get_invitations()

    total_executions = len(executions)

    successful_executions = sum(
        execution.execution_success is True
        for execution in executions
    )

    failed_executions = sum(
        execution.execution_success is False
        for execution in executions
    )

    success_rate = (
        round(successful_executions / total_executions * 100, 2)
        if total_executions else 0.0
    )

    unique_orders = {
        execution.order_id
        for execution in executions
        if execution.order_id is not None
    }

    unique_customers = {
        execution.customer_id
        for execution in executions
        if execution.customer_id is not None
    }

    active_operators = len({
        execution.user_id
        for execution in executions
        if execution.user_id is not None
    })

    error_counts = Counter(
        execution.error_message
        for execution in executions
        if execution.error_message
    )

    # Execution trends
    trends = {
        "daily": defaultdict(Counter),
        "weekly": defaultdict(Counter),
        "monthly": defaultdict(Counter),
    }

    for execution in executions:
        if execution.execution_date is None:
            continue

        date = execution.execution_date.date()

        week = date.isocalendar()

        periods = {
            "daily": date.isoformat(),
            "weekly": f"{week.year}-W{week.week:02d}",
            "monthly": date.strftime("%Y-%m"),
        }

        for period, key in periods.items():
            trends[period][key]["total"] += 1

            if execution.execution_success is True:
                trends[period][key]["successful"] += 1
            elif execution.execution_success is False:
                trends[period][key]["failed"] += 1

    execution_trends = {
        period: {
            key: dict(counts)
            for key, counts in sorted(period_data.items())
        }
        for period, period_data in trends.items()
    }

    return {
        "overview": {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": success_rate,
            "unique_orders_investigated": len(unique_orders),
            "unique_customers_investigated": len(unique_customers),
            "active_operators": active_operators,
        },
        "failure_analytics": {
            "total_failures": failed_executions,
            "common_errors": dict(error_counts.most_common(10)),
        },
        "execution_trends": execution_trends,
        "invitations": {
            "total_invitations": len(invitations),
        },
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_analytics(), sort_dicts=False, indent=4)