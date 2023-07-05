from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.donation import donation_crud


async def func_donation(
        session: AsyncSession,
        object,
):
    project, donation = await donation_crud.get_open_object(session)

    if not project or not donation:
        await session.commit()
        await session.refresh(object)
        return object

    balance_project = project.full_amount - project.invested_amount
    balance_donation = donation.full_amount - donation.invested_amount

    if balance_project > balance_donation:
        project.invested_amount += balance_donation
        donation.invested_amount += balance_donation
        donation.fully_invested = True
        donation.close_date = datetime.now()

    elif balance_project == balance_donation:
        project.invested_amount += balance_donation
        donation.invested_amount += balance_donation
        project.fully_invested = True
        donation.fully_invested = True
        project.close_date = datetime.now()
        donation.close_date = datetime.now()

    elif balance_project < balance_donation:
        project.invested_amount += balance_project
        donation.invested_amount += balance_project
        project.fully_invested = True
        project.close_date = datetime.now()

    session.add(project)
    session.add(donation)
    await session.commit()
    await session.refresh(project)
    await session.refresh(donation)
    await func_donation(session, object)
    return object
