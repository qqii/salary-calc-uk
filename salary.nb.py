import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="full",
    app_title="UK Salary & Pension Calculator",
    auto_download=["html"],
)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # UK Salary & Pension Calculator (2025/26)
    This notebook estimates monthly and annual salary outcomes for UK PAYE with pension, NI, student loans, SSP, health insurance BIK, optimization, and long-term value projection.
    """)
    return


@app.cell(hide_code=True)
def _(
    annual_bonus_ui,
    employee_pension_contribution_ui,
    employer_pension_contribution_ui,
    forecast_inflation_ui,
    forecast_isa_management_fee_ui,
    forecast_market_apy_ui,
    forecast_current_pension_pot_ui,
    forecast_drawdown_years_ui,
    forecast_pension_amc_ui,
    forecast_years_ui,
    gross_income_ui,
    health_insurance_annual_ui,
    health_insurance_toggle_ui,
    holiday_days_ui,
    holiday_rollover_ui,
    mo,
    plan_1_ui,
    plan_2_ui,
    plan_4_ui,
    plan_5_ui,
    postgraduate_ui,
    sick_days_ui,
    sick_pay_type_ui,
    yearly_spend_ui,
):
    input_tabs = {
        "Compensation": mo.vstack(
            [
                gross_income_ui,
                employer_pension_contribution_ui,
                employee_pension_contribution_ui,
            ]
        ),
        "Loans": mo.vstack(
            [
                mo.md("### Student Loan Plans"),
                mo.hstack(
                    [plan_1_ui, plan_2_ui, plan_4_ui, plan_5_ui, postgraduate_ui]
                ),
            ]
        ),
        "Time Off": mo.vstack(
            [
                sick_pay_type_ui,
                sick_days_ui,
                holiday_days_ui,
                holiday_rollover_ui,
            ]
        ),
        "Bonuses": mo.vstack([annual_bonus_ui]),
        "Forecast": mo.vstack(
            [
                forecast_years_ui,
                yearly_spend_ui,
                forecast_current_pension_pot_ui,
                forecast_drawdown_years_ui,
                forecast_market_apy_ui,
                forecast_inflation_ui,
                forecast_pension_amc_ui,
                forecast_isa_management_fee_ui,
            ]
        ),
        "Health Insurance": mo.vstack(
            [
                health_insurance_toggle_ui,
                health_insurance_annual_ui,
            ]
        ),
    }

    mo.output.replace(mo.ui.tabs(input_tabs))
    return


@app.cell(hide_code=True)
def _(
    comparison_section,
    current_breakdown_section,
    forecast_section,
    health_insurance_section,
    mo,
    optimization_section,
    rates_section,
):
    _ = comparison_section
    current_and_rates_section = mo.hstack([current_breakdown_section, rates_section])
    output_tabs = {
        "Current Breakdown": current_and_rates_section,
        "Optimisation": optimization_section,
        "Forecast": forecast_section,
        "Health Insurance": health_insurance_section,
    }
    mo.output.replace(mo.ui.tabs(output_tabs))
    return


@app.cell(hide_code=True)
def _():
    from dataclasses import dataclass, field
    from enum import StrEnum
    from typing import TypeAlias

    import altair as alt
    import marimo as mo
    import polars as pl

    return StrEnum, TypeAlias, alt, dataclass, field, mo, pl


@app.cell(hide_code=True)
def _(StrEnum, TypeAlias, dataclass, field):
    Money: TypeAlias = float
    Rate: TypeAlias = float

    class SickPayType(StrEnum):
        SSP = "ssp"
        CONTRACT = "contract"

    class StudentLoanPlan(StrEnum):
        PLAN_1 = "plan_1"
        PLAN_2 = "plan_2"
        PLAN_4 = "plan_4"
        PLAN_5 = "plan_5"
        POSTGRADUATE = "postgraduate"

    class OptimizationTarget(StrEnum):
        TAKE_HOME = "take_home"
        EFFECTIVE_NET = "effective_net"
        FORECASTED_VALUE = "forecasted_value"

    class InputField(StrEnum):
        GROSS_INCOME = "gross_income"
        ANNUAL_BONUS = "annual_bonus"
        EMPLOYER_PENSION_CONTRIBUTION = "employer_pension_contribution"
        EMPLOYEE_PENSION_CONTRIBUTION = "employee_pension_contribution"
        CURRENT_PENSION_POT = "current_pension_pot"
        SICK_DAYS = "sick_days"
        HOLIDAY_DAYS = "holiday_days"
        HOLIDAY_ROLLOVER = "holiday_rollover"
        HEALTH_INSURANCE_ANNUAL = "health_insurance_annual"
        YEARLY_SPEND = "yearly_spend"

    @dataclass(frozen=True)
    class StudentLoanConfig:
        threshold: Money
        rate: Rate

    @dataclass(frozen=True)
    class TaxRates:
        personal_allowance: Money = 12_570
        personal_allowance_taper_threshold: Money = 100_000
        basic_rate: Rate = 0.20
        basic_rate_upper: Money = 50_270
        higher_rate: Rate = 0.40
        higher_rate_upper: Money = 125_140
        additional_rate: Rate = 0.45
        ni_employee_primary_threshold: Money = 12_570
        ni_employee_upper_earnings_limit: Money = 50_270
        ni_employee_main_rate: Rate = 0.08
        ni_employee_upper_rate: Rate = 0.02
        ni_employer_secondary_threshold: Money = 5_000
        ni_employer_rate: Rate = 0.15
        student_loans: dict[StudentLoanPlan, StudentLoanConfig] = field(
            default_factory=lambda: {
                StudentLoanPlan.PLAN_1: StudentLoanConfig(threshold=26_065, rate=0.09),
                StudentLoanPlan.PLAN_2: StudentLoanConfig(threshold=28_470, rate=0.09),
                StudentLoanPlan.PLAN_4: StudentLoanConfig(threshold=32_745, rate=0.09),
                StudentLoanPlan.PLAN_5: StudentLoanConfig(threshold=25_000, rate=0.09),
                StudentLoanPlan.POSTGRADUATE: StudentLoanConfig(
                    threshold=21_000,
                    rate=0.06,
                ),
            }
        )
        ssp_weekly_rate: Money = 118.75
        ssp_waiting_days: int = 3
        ssp_qualifying_days_per_week: int = 5
        standard_hours_per_day: float = 7.5
        working_days_per_year: int = 260
        min_total_pension_contribution: Rate = 0.08
        nest_contribution_charge: Rate = 0.018

    @dataclass(frozen=True)
    class CalcOptions:
        student_loan_plans: tuple[StudentLoanPlan, ...] = ()
        sick_pay_type: SickPayType = SickPayType.CONTRACT
        sick_days_per_year: int = 0
        holiday_days: int = 28
        health_insurance_annual: Money = 0.0
        health_insurance_bik: Money = 0.0

    @dataclass(frozen=True)
    class CalcInputs:
        gross: Money
        employer_prc: Rate
        employee_prc: Rate

    @dataclass(frozen=True)
    class CalcDetails:
        employee_pension_contribution: Money
        employer_pension_contribution: Money
        gov_pension_contribution: Money
        national_insurance: Money
        student_loan: Money
        tax: Money
        employer_national_insurance: Money
        ssp_deduction: Money
        health_insurance_bik_tax: Money

    @dataclass(frozen=True)
    class AnnualSummary:
        gross: Money
        net_pay: Money
        tax: Money
        ni: Money
        student_loan: Money
        employer_total: Money
        ssp_deduction: Money

    @dataclass(frozen=True)
    class RateSummary:
        effective_daily_rate: Money
        effective_hourly_rate: Money
        effective_weekly_rate: Money
        effective_monthly_rate: Money
        effective_working_days: int
        holiday_days: int
        gross_daily_rate: Money
        gross_hourly_rate: Money
        gross_weekly_rate: Money
        gross_monthly_rate: Money

    @dataclass(frozen=True)
    class CalcResult:
        theoretical_net: Money
        net_pay: Money
        total_pension_contribution: Money
        employer_total_outgoing: Money
        inputs: CalcInputs
        details: CalcDetails
        annual: AnnualSummary
        rates: RateSummary

    @dataclass(frozen=True)
    class HealthInsuranceBenchmark:
        as_of: str
        axa_monthly_estimate: Money
        vitality_monthly_estimate: Money
        blended_monthly_estimate: Money
        vitality_source: str
        axa_source: str
        axa_benchmark_source: str

    @dataclass(frozen=True)
    class IsaBreakdown:
        lifetime_isa_contribution: Money
        lifetime_isa_total: Money
        normal_isa_contribution: Money
        sipp_contribution: Money

    @dataclass(frozen=True)
    class OptimizationOutcome:
        result: CalcResult | None
        reason: str | None

    @dataclass(frozen=True)
    class ValidationBounds:
        min_gross_income: Money = 10_000
        max_gross_income: Money = 200_000
        max_annual_bonus: Money = 200_000
        max_pension_contribution: Rate = 0.5
        max_sick_days: int = 30
        min_holiday_days: int = 28
        max_holiday_days: int = 45
        max_holiday_rollover: int = 10
        max_health_insurance_annual: Money = 5_000
        min_yearly_spend: Money = 10_000
        max_yearly_spend: Money = 80_000
        max_current_pension_pot: Money = 5_000_000

    @dataclass(frozen=True)
    class FieldSpec:
        key: InputField
        label: str
        default: float | int
        minimum: float | None = None
        maximum: float | None = None
        integer: bool = False
        range_message: str | None = None

    @dataclass(frozen=True)
    class InputDefaults:
        gross_income: Money = 48_000
        annual_bonus: Money = 250
        employer_pension_contribution: Rate = 0.08
        employee_pension_contribution: Rate = 0.04
        current_pension_pot: Money = 32_000
        sick_pay_type: SickPayType = SickPayType.CONTRACT
        sick_days: int = 5
        holiday_days: int = 40
        holiday_rollover: int = 3
        health_insurance_toggle: bool = True
        plan_1_enabled: bool = False
        plan_2_enabled: bool = True
        plan_4_enabled: bool = False
        plan_5_enabled: bool = False
        postgraduate_enabled: bool = False
        yearly_spend: Money = 32_000
        forecast_drawdown_years: int = 25
        optimize_target: OptimizationTarget = OptimizationTarget.FORECASTED_VALUE
        optimize_search_all_three: bool = False
        forecast_use_optimized: bool = True

    @dataclass(frozen=True)
    class UserInputs:
        gross_income: Money
        annual_bonus: Money
        employer_pension_contribution: Rate
        employee_pension_contribution: Rate
        current_pension_pot: Money
        sick_days: int
        holiday_days: int
        holiday_rollover: int
        health_insurance_annual: Money
        health_insurance_toggle: bool
        yearly_spend: Money

    @dataclass(frozen=True)
    class ForecastAssumptions:
        years: int = 39
        average_market_apy: Rate = 0.06
        average_inflation: Rate = 0.03
        pension_amc: Rate = 0.003
        isa_management_fee: Rate = 0.005

    return (
        AnnualSummary,
        CalcDetails,
        CalcInputs,
        CalcOptions,
        CalcResult,
        FieldSpec,
        ForecastAssumptions,
        HealthInsuranceBenchmark,
        InputDefaults,
        InputField,
        IsaBreakdown,
        OptimizationTarget,
        OptimizationOutcome,
        RateSummary,
        SickPayType,
        StudentLoanPlan,
        TaxRates,
        UserInputs,
        ValidationBounds,
    )


@app.cell(hide_code=True)
def _(
    ForecastAssumptions,
    HealthInsuranceBenchmark,
    InputDefaults,
    TaxRates,
    ValidationBounds,
):
    MONTHS_PER_YEAR = 12
    HOURS_PER_WEEK = 40
    WEEKS_PER_YEAR = 52

    TAX_RATES = TaxRates()
    VALIDATION_BOUNDS = ValidationBounds()
    FORECAST_ASSUMPTIONS = ForecastAssumptions()
    INPUT_DEFAULTS = InputDefaults()

    vitality_monthly_estimate = 44.0
    axa_monthly_estimate = 120.75
    blended_monthly_estimate = (axa_monthly_estimate + vitality_monthly_estimate) / 2
    HEALTH_INSURANCE_BENCHMARK = HealthInsuranceBenchmark(
        as_of="2026-02-17",
        axa_monthly_estimate=axa_monthly_estimate,
        vitality_monthly_estimate=vitality_monthly_estimate,
        blended_monthly_estimate=blended_monthly_estimate,
        vitality_source="https://www.vitality.co.uk/health-insurance/",
        axa_source="https://www.axahealth.co.uk/",
        axa_benchmark_source="https://www.forbes.com/advisor/uk/health-insurance/",
    )
    return (
        FORECAST_ASSUMPTIONS,
        HEALTH_INSURANCE_BENCHMARK,
        HOURS_PER_WEEK,
        INPUT_DEFAULTS,
        MONTHS_PER_YEAR,
        TAX_RATES,
        VALIDATION_BOUNDS,
        WEEKS_PER_YEAR,
    )


@app.cell(hide_code=True)
def _():
    def p(amount: float) -> str:
        rounded = round(amount + (1e-12 if amount >= 0 else -1e-12), 2)
        prefix = "-£" if rounded < 0 else "£"
        return f"{prefix}{abs(rounded):,.2f}"

    def c(ratio: float) -> str:
        return f"{ratio * 100:.2f}%"

    return c, p


@app.cell(hide_code=True)
def _(
    CalcOptions,
    HOURS_PER_WEEK,
    MONTHS_PER_YEAR,
    RateSummary,
    SickPayType,
    StudentLoanPlan,
    TaxRates,
    WEEKS_PER_YEAR,
):
    def compute_income_tax(annual_gross: float, rates: TaxRates) -> float:
        personal_allowance = rates.personal_allowance
        if annual_gross > rates.personal_allowance_taper_threshold:
            taper = (annual_gross - rates.personal_allowance_taper_threshold) / 2
            personal_allowance = max(0.0, personal_allowance - taper)

        taxable_remaining = max(0.0, annual_gross)

        at_allowance = min(taxable_remaining, personal_allowance)
        taxable_remaining -= at_allowance

        basic_limit = max(0.0, rates.basic_rate_upper - personal_allowance)
        at_basic = min(taxable_remaining, basic_limit)
        tax = at_basic * rates.basic_rate
        taxable_remaining -= at_basic

        higher_limit = rates.higher_rate_upper - rates.basic_rate_upper
        at_higher = min(taxable_remaining, higher_limit)
        tax += at_higher * rates.higher_rate
        taxable_remaining -= at_higher

        tax += taxable_remaining * rates.additional_rate
        return tax

    def compute_employee_ni(annual_gross: float, rates: TaxRates) -> float:
        if annual_gross <= rates.ni_employee_primary_threshold:
            return 0.0

        earnings_in_main_band = (
            min(annual_gross, rates.ni_employee_upper_earnings_limit)
            - rates.ni_employee_primary_threshold
        )
        earnings_in_upper_band = max(
            0.0,
            annual_gross - rates.ni_employee_upper_earnings_limit,
        )

        return (
            earnings_in_main_band * rates.ni_employee_main_rate
            + earnings_in_upper_band * rates.ni_employee_upper_rate
        )

    def compute_employer_ni(annual_gross: float, rates: TaxRates) -> float:
        if annual_gross <= rates.ni_employer_secondary_threshold:
            return 0.0
        return (
            annual_gross - rates.ni_employer_secondary_threshold
        ) * rates.ni_employer_rate

    def compute_student_loan(
        annual_gross: float,
        plan_types: tuple[StudentLoanPlan, ...],
        rates: TaxRates,
    ) -> float:
        total = 0.0
        for plan in plan_types:
            config = rates.student_loans.get(plan)
            if config and annual_gross > config.threshold:
                total += (annual_gross - config.threshold) * config.rate
        return total

    def compute_pension_parts(
        annual_gross: float,
        employer_prc: float,
        employee_prc: float,
    ) -> tuple[float, float, float, float]:
        annual_employee_pension = annual_gross * employee_prc
        annual_government_top_up = 0.0
        annual_employer_pension = annual_gross * employer_prc
        annual_total_pension = (
            annual_employee_pension + annual_government_top_up + annual_employer_pension
        )

        return (
            annual_employee_pension,
            annual_government_top_up,
            annual_employer_pension,
            annual_total_pension,
        )

    def compute_ssp_deduction(
        annual_gross: float,
        options: CalcOptions,
        rates: TaxRates,
    ) -> float:
        if options.sick_pay_type != SickPayType.SSP or options.sick_days_per_year <= 0:
            return 0.0

        contractual_days = max(1, rates.working_days_per_year)
        daily_gross = annual_gross / contractual_days
        ssp_daily = rates.ssp_weekly_rate / rates.ssp_qualifying_days_per_week
        waiting_days = min(options.sick_days_per_year, rates.ssp_waiting_days)
        paid_sick_days = max(0, options.sick_days_per_year - rates.ssp_waiting_days)

        paid_day_loss = max(0.0, daily_gross - ssp_daily)
        return waiting_days * daily_gross + paid_sick_days * paid_day_loss

    def compute_effective_rates(
        annual_gross: float,
        annual_net_after_ssp: float,
        options: CalcOptions,
        rates: TaxRates,
    ) -> RateSummary:
        working_days = max(0, rates.working_days_per_year - options.holiday_days)
        effective_working_days = max(0, working_days - options.sick_days_per_year)

        if effective_working_days == 0:
            return RateSummary(
                effective_daily_rate=0.0,
                effective_hourly_rate=0.0,
                effective_weekly_rate=0.0,
                effective_monthly_rate=0.0,
                effective_working_days=0,
                holiday_days=options.holiday_days,
                gross_daily_rate=0.0,
                gross_hourly_rate=0.0,
                gross_weekly_rate=0.0,
                gross_monthly_rate=0.0,
            )

        effective_daily_rate = annual_net_after_ssp / effective_working_days
        gross_daily_rate = annual_gross / effective_working_days
        effective_hourly_rate = effective_daily_rate / rates.standard_hours_per_day
        gross_hourly_rate = gross_daily_rate / rates.standard_hours_per_day
        effective_weekly_rate = effective_hourly_rate * HOURS_PER_WEEK
        gross_weekly_rate = gross_hourly_rate * HOURS_PER_WEEK

        return RateSummary(
            effective_daily_rate=effective_daily_rate,
            effective_hourly_rate=effective_hourly_rate,
            effective_weekly_rate=effective_weekly_rate,
            effective_monthly_rate=effective_weekly_rate
            * WEEKS_PER_YEAR
            / MONTHS_PER_YEAR,
            effective_working_days=effective_working_days,
            holiday_days=options.holiday_days,
            gross_daily_rate=gross_daily_rate,
            gross_hourly_rate=gross_hourly_rate,
            gross_weekly_rate=gross_weekly_rate,
            gross_monthly_rate=gross_weekly_rate * WEEKS_PER_YEAR / MONTHS_PER_YEAR,
        )

    return (
        compute_effective_rates,
        compute_employee_ni,
        compute_employer_ni,
        compute_income_tax,
        compute_pension_parts,
        compute_ssp_deduction,
        compute_student_loan,
    )


@app.cell(hide_code=True)
def _(
    AnnualSummary,
    CalcDetails,
    CalcInputs,
    CalcOptions,
    CalcResult,
    MONTHS_PER_YEAR,
    TAX_RATES,
    compute_effective_rates,
    compute_employee_ni,
    compute_employer_ni,
    compute_income_tax,
    compute_pension_parts,
    compute_ssp_deduction,
    compute_student_loan,
):
    def calc_pay_ras(
        monthly_gross_income: float,
        employer_prc: float,
        employee_prc: float,
        options: CalcOptions | None = None,
    ) -> CalcResult:
        opts = options or CalcOptions()

        annual_contractual_gross = monthly_gross_income * MONTHS_PER_YEAR
        annual_ssp_deduction = compute_ssp_deduction(
            annual_contractual_gross, opts, TAX_RATES
        )
        annual_paid_gross = max(0.0, annual_contractual_gross - annual_ssp_deduction)

        (
            annual_employee_pension,
            annual_government_top_up,
            annual_employer_pension,
            annual_total_pension,
        ) = compute_pension_parts(annual_paid_gross, employer_prc, employee_prc)
        annual_taxable_without_bik = max(0.0, annual_paid_gross - annual_employee_pension)
        annual_taxable = annual_taxable_without_bik + opts.health_insurance_bik

        annual_ni = compute_employee_ni(annual_paid_gross, TAX_RATES)
        annual_student_loan = compute_student_loan(
            annual_paid_gross,
            opts.student_loan_plans,
            TAX_RATES,
        )
        annual_tax = compute_income_tax(annual_taxable, TAX_RATES)

        annual_net_after_ssp = (
            annual_paid_gross
            - annual_employee_pension
            - annual_ni
            - annual_student_loan
            - annual_tax
        )

        annual_employer_ni = compute_employer_ni(annual_paid_gross, TAX_RATES)
        annual_bik_ni = opts.health_insurance_bik * TAX_RATES.ni_employer_rate
        annual_employer_total = (
            annual_paid_gross
            + annual_employer_pension
            + annual_employer_ni
            + opts.health_insurance_annual
            + annual_bik_ni
        )

        rates = compute_effective_rates(
            annual_paid_gross, annual_net_after_ssp, opts, TAX_RATES
        )

        monthly_net = annual_net_after_ssp / MONTHS_PER_YEAR
        monthly_pension = annual_total_pension / MONTHS_PER_YEAR
        monthly_bik_tax = (
            compute_income_tax(annual_taxable, TAX_RATES)
            - compute_income_tax(annual_taxable_without_bik, TAX_RATES)
        ) / MONTHS_PER_YEAR

        return CalcResult(
            theoretical_net=monthly_net + monthly_pension,
            net_pay=monthly_net,
            total_pension_contribution=monthly_pension,
            employer_total_outgoing=annual_employer_total / MONTHS_PER_YEAR,
            inputs=CalcInputs(
                gross=monthly_gross_income,
                employer_prc=employer_prc,
                employee_prc=employee_prc,
            ),
            details=CalcDetails(
                employee_pension_contribution=annual_employee_pension / MONTHS_PER_YEAR,
                employer_pension_contribution=annual_employer_pension / MONTHS_PER_YEAR,
                gov_pension_contribution=annual_government_top_up / MONTHS_PER_YEAR,
                national_insurance=annual_ni / MONTHS_PER_YEAR,
                student_loan=annual_student_loan / MONTHS_PER_YEAR,
                tax=annual_tax / MONTHS_PER_YEAR,
                employer_national_insurance=annual_employer_ni / MONTHS_PER_YEAR,
                ssp_deduction=annual_ssp_deduction / MONTHS_PER_YEAR,
                health_insurance_bik_tax=(
                    monthly_bik_tax if opts.health_insurance_bik > 0 else 0.0
                ),
            ),
            annual=AnnualSummary(
                gross=annual_contractual_gross,
                net_pay=annual_net_after_ssp,
                tax=annual_tax,
                ni=annual_ni,
                student_loan=annual_student_loan,
                employer_total=annual_employer_total,
                ssp_deduction=annual_ssp_deduction,
            ),
            rates=rates,
        )

    def income_tax(annual_gross: float) -> float:
        return compute_income_tax(annual_gross, TAX_RATES)

    return calc_pay_ras, income_tax


@app.cell(hide_code=True)
def _(
    CalcOptions,
    CalcResult,
    OptimizationOutcome,
    TAX_RATES,
    VALIDATION_BOUNDS,
    calc_pay_ras,
):
    def frange(start: float, stop: float, step: float) -> tuple[float, ...]:
        span = max(0.0, stop - start)
        steps = round(span / step)
        return tuple(round(start + index * step, 12) for index in range(steps + 1))

    def optimize_proposal(
        curr: CalcResult,
        yearly_spend: float,
        options: CalcOptions,
        *,
        objective_fn=None,
        search_salary_employer_employee: bool = False,
    ) -> OptimizationOutcome:
        objective = objective_fn or (lambda proposal: proposal.theoretical_net)
        current_annual_gross = curr.inputs.gross * 12
        fixed_employer_rate = curr.inputs.employer_prc

        def gross_values(start: float, stop: float, step: float) -> tuple[float, ...]:
            tolerance = 1e-9
            if abs(stop - start) < tolerance:
                return (start,)
            return frange(start, stop, step)

        def employer_values(
            start: float, stop: float, step: float
        ) -> tuple[float, ...]:
            tolerance = 1e-9
            if abs(stop - start) < tolerance:
                return (start,)
            return frange(start, stop, step)

        def find_best(
            annual_gross_start: float,
            annual_gross_stop: float,
            annual_gross_step: float,
            employer_start: float,
            employer_stop: float,
            employer_step: float,
            employee_start: float,
            employee_stop: float,
            employee_step: float,
        ) -> tuple[CalcResult | None, float, float, float]:
            best_result: CalcResult | None = None
            best_annual_gross = annual_gross_start
            best_employer_rate = employer_start
            best_employee_rate = employee_start
            best_objective = float("-inf")

            for annual_gross in gross_values(
                annual_gross_start,
                annual_gross_stop,
                annual_gross_step,
            ):
                monthly_gross = annual_gross / 12
                for employer_rate in employer_values(
                    employer_start,
                    employer_stop,
                    employer_step,
                ):
                    for employee_rate in frange(
                        employee_start,
                        employee_stop,
                        employee_step,
                    ):
                        if (
                            employer_rate + employee_rate
                            < TAX_RATES.min_total_pension_contribution
                        ):
                            continue
                        proposal = calc_pay_ras(
                            monthly_gross,
                            employer_rate,
                            employee_rate,
                            options,
                        )
                        if (
                            proposal.employer_total_outgoing
                            > curr.employer_total_outgoing
                        ):
                            break
                        if proposal.net_pay * 12 < yearly_spend:
                            continue
                        objective_value = objective(proposal)
                        if objective_value <= best_objective:
                            continue

                        best_result = proposal
                        best_annual_gross = annual_gross
                        best_employer_rate = employer_rate
                        best_employee_rate = employee_rate
                        best_objective = objective_value

            return (
                best_result,
                best_annual_gross,
                best_employer_rate,
                best_employee_rate,
            )

        if search_salary_employer_employee:
            gross_floor = max(
                VALIDATION_BOUNDS.min_gross_income,
                current_annual_gross * 0.7,
            )
            gross_ceiling = min(
                VALIDATION_BOUNDS.max_gross_income,
                current_annual_gross * 1.3,
            )
            employer_floor = 0.0
            employer_ceiling = VALIDATION_BOUNDS.max_pension_contribution
        else:
            gross_floor = current_annual_gross
            gross_ceiling = current_annual_gross
            employer_floor = fixed_employer_rate
            employer_ceiling = fixed_employer_rate

        best_result, best_annual_gross, best_employer_rate, best_employee_rate = (
            find_best(
                annual_gross_start=gross_floor,
                annual_gross_stop=gross_ceiling,
                annual_gross_step=2_500 if search_salary_employer_employee else 1.0,
                employer_start=employer_floor,
                employer_stop=employer_ceiling,
                employer_step=0.04 if search_salary_employer_employee else 1.0,
                employee_start=0.0,
                employee_stop=0.5,
                employee_step=0.02,
            )
        )

        if best_result:
            best_result, best_annual_gross, best_employer_rate, best_employee_rate = (
                find_best(
                    annual_gross_start=(
                        max(gross_floor, best_annual_gross - 3_000)
                        if search_salary_employer_employee
                        else current_annual_gross
                    ),
                    annual_gross_stop=(
                        min(gross_ceiling, best_annual_gross + 3_000)
                        if search_salary_employer_employee
                        else current_annual_gross
                    ),
                    annual_gross_step=500 if search_salary_employer_employee else 1.0,
                    employer_start=(
                        max(employer_floor, best_employer_rate - 0.08)
                        if search_salary_employer_employee
                        else fixed_employer_rate
                    ),
                    employer_stop=(
                        min(employer_ceiling, best_employer_rate + 0.08)
                        if search_salary_employer_employee
                        else fixed_employer_rate
                    ),
                    employer_step=0.01 if search_salary_employer_employee else 1.0,
                    employee_start=max(0.0, best_employee_rate - 0.08),
                    employee_stop=min(0.5, best_employee_rate + 0.08),
                    employee_step=0.01,
                )
            )

        if best_result:
            best_result, _, _, _ = find_best(
                annual_gross_start=(
                    max(gross_floor, best_annual_gross - 1_000)
                    if search_salary_employer_employee
                    else current_annual_gross
                ),
                annual_gross_stop=(
                    min(gross_ceiling, best_annual_gross + 1_000)
                    if search_salary_employer_employee
                    else current_annual_gross
                ),
                annual_gross_step=100 if search_salary_employer_employee else 1.0,
                employer_start=(
                    max(employer_floor, best_employer_rate - 0.02)
                    if search_salary_employer_employee
                    else fixed_employer_rate
                ),
                employer_stop=(
                    min(employer_ceiling, best_employer_rate + 0.02)
                    if search_salary_employer_employee
                    else fixed_employer_rate
                ),
                employer_step=0.005 if search_salary_employer_employee else 1.0,
                employee_start=max(0.0, best_employee_rate - 0.02),
                employee_stop=min(0.5, best_employee_rate + 0.02),
                employee_step=0.002,
            )

        if best_result:
            return OptimizationOutcome(result=best_result, reason=None)

        return OptimizationOutcome(
            result=None,
            reason="Cannot meet constraints with current salary and spending target.",
        )

    return (optimize_proposal,)


@app.cell(hide_code=True)
def _(FORECAST_ASSUMPTIONS, IsaBreakdown, income_tax):
    def isa_contribution(net_pay: float, yearly_spending: float) -> IsaBreakdown:
        maximum_lifetime_isa = 4_000
        lifetime_isa_bonus_multiplier = 1.25
        maximum_isa_total = 20_000

        isa_total = min(max(0.0, net_pay - yearly_spending), maximum_isa_total)
        lifetime_isa_contribution = min(isa_total, maximum_lifetime_isa)
        lifetime_isa_total = lifetime_isa_contribution * lifetime_isa_bonus_multiplier
        normal_isa_contribution = isa_total - lifetime_isa_contribution
        sipp_contribution = max(0.0, net_pay - yearly_spending - isa_total)

        return IsaBreakdown(
            lifetime_isa_contribution=lifetime_isa_contribution,
            lifetime_isa_total=lifetime_isa_total,
            normal_isa_contribution=normal_isa_contribution,
            sipp_contribution=sipp_contribution,
        )

    def forecast_terminal_value(
        net_pay: float,
        total_pension_contribution: float,
        yearly_spend: float,
        current_pension_pot: float,
        drawdown_years: int,
        years: int,
        market_apy: float,
        inflation: float,
        pension_amc: float,
        isa_management_fee: float,
    ) -> float:
        monthly_spending = yearly_spend / 12
        can_invest = net_pay >= monthly_spending

        pension_growth_rate = (1 - pension_amc) * (1 - inflation) * (1 + market_apy) - 1
        isa_growth_rate = (1 - isa_management_fee) * (1 - inflation) * (
            1 + market_apy
        ) - 1
        isa = isa_contribution(net_pay * 12, yearly_spend)
        annual_pension_contribution = total_pension_contribution * 12
        annual_isa_total_contribution = (
            isa.lifetime_isa_total + isa.normal_isa_contribution + isa.sipp_contribution
            if can_invest
            else 0.0
        )
        annual_isa_taxable_contribution = isa.sipp_contribution if can_invest else 0.0

        def _tax_from_taxable_pot(taxable_pot: float) -> float:
            if taxable_pot <= 0:
                return 0.0
            years_to_draw = max(1, int(drawdown_years))
            target_taxable_per_year = max(0.0, yearly_spend * 0.75)
            tolerance = 1e-9
            remaining = taxable_pot
            total_tax = 0.0

            for year_index in range(years_to_draw):
                years_left = years_to_draw - year_index
                minimum_to_finish = remaining / years_left
                annual_taxable = min(
                    remaining,
                    max(target_taxable_per_year, minimum_to_finish),
                )
                total_tax += income_tax(annual_taxable)
                remaining -= annual_taxable
                if remaining <= tolerance:
                    break

            return total_tax

        pension_gross = current_pension_pot + annual_pension_contribution
        isa_gross = annual_isa_total_contribution
        isa_taxable_gross = annual_isa_taxable_contribution

        for _ in range(1, years + 1):
            pension_gross = (pension_gross + annual_pension_contribution) * (
                1 + pension_growth_rate
            )
            isa_gross = (isa_gross + annual_isa_total_contribution) * (
                1 + isa_growth_rate
            )
            isa_taxable_gross = (
                isa_taxable_gross + annual_isa_taxable_contribution
            ) * (1 + isa_growth_rate)

        pension_net = pension_gross - _tax_from_taxable_pot(0.75 * pension_gross)
        isa_net = isa_gross - _tax_from_taxable_pot(isa_taxable_gross)
        return pension_net + isa_net

    def forecast_projection(
        net_pay: float,
        total_pension_contribution: float,
        yearly_spend: float,
        current_pension_pot: float,
        drawdown_years: int,
        years: int,
        market_apy: float,
        inflation: float,
        pension_amc: float,
        isa_management_fee: float,
    ) -> tuple[dict[str, float], ...]:
        monthly_spending = yearly_spend / 12
        can_invest = net_pay >= monthly_spending

        pension_growth_rate = (1 - pension_amc) * (1 - inflation) * (1 + market_apy) - 1
        isa_growth_rate = (1 - isa_management_fee) * (1 - inflation) * (
            1 + market_apy
        ) - 1
        isa = isa_contribution(net_pay * 12, yearly_spend)
        annual_pension_contribution = total_pension_contribution * 12
        annual_isa_total_contribution = (
            isa.lifetime_isa_total + isa.normal_isa_contribution + isa.sipp_contribution
            if can_invest
            else 0.0
        )
        annual_isa_taxable_contribution = isa.sipp_contribution if can_invest else 0.0

        def _tax_from_taxable_pot(taxable_pot: float) -> float:
            if taxable_pot <= 0:
                return 0.0
            years_to_draw = max(1, int(drawdown_years))
            target_taxable_per_year = max(0.0, yearly_spend * 0.75)
            tolerance = 1e-9
            remaining = taxable_pot
            total_tax = 0.0

            for year_index in range(years_to_draw):
                years_left = years_to_draw - year_index
                minimum_to_finish = remaining / years_left
                annual_taxable = min(
                    remaining,
                    max(target_taxable_per_year, minimum_to_finish),
                )
                total_tax += income_tax(annual_taxable)
                remaining -= annual_taxable
                if remaining <= tolerance:
                    break

            return total_tax

        pension_gross = current_pension_pot + annual_pension_contribution
        isa_gross = annual_isa_total_contribution
        isa_taxable_gross = annual_isa_taxable_contribution
        pension_net = pension_gross - _tax_from_taxable_pot(0.75 * pension_gross)
        isa_net = isa_gross - _tax_from_taxable_pot(isa_taxable_gross)
        rows: list[dict[str, float]] = [
            {
                "year": 0.0,
                "pension_net": pension_net,
                "isa_net": isa_net,
                "total_net": pension_net + isa_net,
            }
        ]

        for year in range(1, years + 1):
            pension_gross = (pension_gross + annual_pension_contribution) * (
                1 + pension_growth_rate
            )
            pension_net = pension_gross - _tax_from_taxable_pot(0.75 * pension_gross)

            isa_gross = (isa_gross + annual_isa_total_contribution) * (
                1 + isa_growth_rate
            )
            isa_taxable_gross = (
                isa_taxable_gross + annual_isa_taxable_contribution
            ) * (1 + isa_growth_rate)
            isa_net = isa_gross - _tax_from_taxable_pot(isa_taxable_gross)

            rows.append(
                {
                    "year": float(year),
                    "pension_net": pension_net,
                    "isa_net": isa_net,
                    "total_net": pension_net + isa_net,
                }
            )

        return tuple(rows)

    def forecast(
        net_pay: float,
        total_pension_contribution: float,
        yearly_spend: float,
    ) -> float:
        return forecast_terminal_value(
            net_pay=net_pay,
            total_pension_contribution=total_pension_contribution,
            yearly_spend=yearly_spend,
            current_pension_pot=0.0,
            drawdown_years=25,
            years=FORECAST_ASSUMPTIONS.years,
            market_apy=FORECAST_ASSUMPTIONS.average_market_apy,
            inflation=FORECAST_ASSUMPTIONS.average_inflation,
            pension_amc=FORECAST_ASSUMPTIONS.pension_amc,
            isa_management_fee=FORECAST_ASSUMPTIONS.isa_management_fee,
        )

    return forecast, forecast_projection, forecast_terminal_value


@app.cell(hide_code=True)
def _(
    FORECAST_ASSUMPTIONS,
    HEALTH_INSURANCE_BENCHMARK,
    INPUT_DEFAULTS,
    SickPayType,
    VALIDATION_BOUNDS,
    mo,
):
    estimated_health_insurance_annual = round(
        12 * HEALTH_INSURANCE_BENCHMARK.blended_monthly_estimate,
        2,
    )

    gross_income_ui = mo.ui.number(
        value=INPUT_DEFAULTS.gross_income,
        label="Gross Yearly Salary (£)",
    )
    employer_pension_contribution_ui = mo.ui.number(
        value=INPUT_DEFAULTS.employer_pension_contribution,
        step=0.01,
        label="Employer Pension Contribution (0-1)",
    )
    employee_pension_contribution_ui = mo.ui.number(
        value=INPUT_DEFAULTS.employee_pension_contribution,
        step=0.01,
        label="Employee Pension Contribution (0-1)",
    )
    yearly_spend_ui = mo.ui.number(
        value=INPUT_DEFAULTS.yearly_spend,
        label="Approximate Yearly Spending (£)",
    )
    annual_bonus_ui = mo.ui.number(
        value=INPUT_DEFAULTS.annual_bonus,
        label="Flat Bonus (£/year)",
    )

    sick_pay_options = {
        "Full Contract Pay": SickPayType.CONTRACT.value,
        "Statutory Sick Pay (SSP)": SickPayType.SSP.value,
    }
    default_sick_pay_label = next(
        label
        for label, sick_pay_value in sick_pay_options.items()
        if sick_pay_value == INPUT_DEFAULTS.sick_pay_type.value
    )

    sick_pay_type_ui = mo.ui.radio(
        options=sick_pay_options,
        value=default_sick_pay_label,
        label="Sick Pay Type",
    )
    sick_days_ui = mo.ui.number(
        value=INPUT_DEFAULTS.sick_days,
        step=1,
        label="Estimated Sick Days/Year",
    )
    holiday_days_ui = mo.ui.number(
        start=VALIDATION_BOUNDS.min_holiday_days,
        stop=VALIDATION_BOUNDS.max_holiday_days,
        value=INPUT_DEFAULTS.holiday_days,
        step=1,
        label="Holiday Days",
    )
    holiday_rollover_ui = mo.ui.number(
        value=INPUT_DEFAULTS.holiday_rollover,
        step=1,
        label="Holiday Rollover Days",
    )

    health_insurance_toggle_ui = mo.ui.checkbox(
        label="Use Employer Benefits (unchecked = Personal Insurance)",
        value=INPUT_DEFAULTS.health_insurance_toggle,
    )
    health_insurance_annual_ui = mo.ui.number(
        value=estimated_health_insurance_annual,
        label="Estimated Health Insurance Premium (£/year, editable)",
    )

    plan_1_ui = mo.ui.checkbox(label="Plan 1", value=INPUT_DEFAULTS.plan_1_enabled)
    plan_2_ui = mo.ui.checkbox(label="Plan 2", value=INPUT_DEFAULTS.plan_2_enabled)
    plan_4_ui = mo.ui.checkbox(
        label="Plan 4 (Scotland)",
        value=INPUT_DEFAULTS.plan_4_enabled,
    )
    plan_5_ui = mo.ui.checkbox(label="Plan 5", value=INPUT_DEFAULTS.plan_5_enabled)
    postgraduate_ui = mo.ui.checkbox(
        label="Postgraduate",
        value=INPUT_DEFAULTS.postgraduate_enabled,
    )

    forecast_years_ui = mo.ui.number(
        value=FORECAST_ASSUMPTIONS.years,
        step=1,
        label="Projection Years",
    )
    forecast_current_pension_pot_ui = mo.ui.number(
        value=INPUT_DEFAULTS.current_pension_pot,
        label="Current Pension Pot (£)",
    )
    forecast_drawdown_years_ui = mo.ui.number(
        value=INPUT_DEFAULTS.forecast_drawdown_years,
        step=1,
        label="Pension Drawdown Years",
    )
    forecast_market_apy_ui = mo.ui.number(
        value=FORECAST_ASSUMPTIONS.average_market_apy,
        step=0.005,
        label="Expected Market APY (0-1)",
    )
    forecast_inflation_ui = mo.ui.number(
        value=FORECAST_ASSUMPTIONS.average_inflation,
        step=0.005,
        label="Expected Inflation (0-1)",
    )
    forecast_pension_amc_ui = mo.ui.number(
        value=FORECAST_ASSUMPTIONS.pension_amc,
        step=0.0005,
        label="Pension AMC (0-1)",
    )
    forecast_isa_management_fee_ui = mo.ui.number(
        value=FORECAST_ASSUMPTIONS.isa_management_fee,
        step=0.0005,
        label="ISA Management Fee (0-1)",
    )
    return (
        annual_bonus_ui,
        employee_pension_contribution_ui,
        employer_pension_contribution_ui,
        forecast_current_pension_pot_ui,
        forecast_drawdown_years_ui,
        forecast_inflation_ui,
        forecast_isa_management_fee_ui,
        forecast_market_apy_ui,
        forecast_pension_amc_ui,
        forecast_years_ui,
        gross_income_ui,
        health_insurance_annual_ui,
        health_insurance_toggle_ui,
        holiday_days_ui,
        holiday_rollover_ui,
        plan_1_ui,
        plan_2_ui,
        plan_4_ui,
        plan_5_ui,
        postgraduate_ui,
        sick_days_ui,
        sick_pay_type_ui,
        yearly_spend_ui,
    )


@app.cell(hide_code=True)
def _(
    CalcOptions,
    FieldSpec,
    INPUT_DEFAULTS,
    InputField,
    SickPayType,
    StudentLoanPlan,
    TAX_RATES,
    UserInputs,
    VALIDATION_BOUNDS,
    annual_bonus_ui,
    employee_pension_contribution_ui,
    employer_pension_contribution_ui,
    forecast_current_pension_pot_ui,
    gross_income_ui,
    health_insurance_annual_ui,
    health_insurance_toggle_ui,
    holiday_days_ui,
    holiday_rollover_ui,
    mo,
    plan_1_ui,
    plan_2_ui,
    plan_4_ui,
    plan_5_ui,
    postgraduate_ui,
    sick_days_ui,
    sick_pay_type_ui,
    yearly_spend_ui,
):
    field_specs = (
        FieldSpec(
            key=InputField.GROSS_INCOME,
            label="Gross yearly salary",
            default=INPUT_DEFAULTS.gross_income,
            minimum=VALIDATION_BOUNDS.min_gross_income,
            maximum=VALIDATION_BOUNDS.max_gross_income,
            range_message=(
                f"Gross yearly salary must be between "
                f"{VALIDATION_BOUNDS.min_gross_income:,.0f} and "
                f"{VALIDATION_BOUNDS.max_gross_income:,.0f}."
            ),
        ),
        FieldSpec(
            key=InputField.ANNUAL_BONUS,
            label="Flat annual bonus",
            default=INPUT_DEFAULTS.annual_bonus,
            minimum=0,
            maximum=VALIDATION_BOUNDS.max_annual_bonus,
            range_message=(
                f"Flat annual bonus must be between 0 and "
                f"{VALIDATION_BOUNDS.max_annual_bonus:,.0f}."
            ),
        ),
        FieldSpec(
            key=InputField.EMPLOYER_PENSION_CONTRIBUTION,
            label="Employer pension contribution",
            default=INPUT_DEFAULTS.employer_pension_contribution,
            minimum=0.0,
            maximum=VALIDATION_BOUNDS.max_pension_contribution,
            range_message=(
                f"Employer pension contribution must be between 0.0 and "
                f"{VALIDATION_BOUNDS.max_pension_contribution:g}."
            ),
        ),
        FieldSpec(
            key=InputField.EMPLOYEE_PENSION_CONTRIBUTION,
            label="Employee pension contribution",
            default=INPUT_DEFAULTS.employee_pension_contribution,
            minimum=0.0,
            maximum=VALIDATION_BOUNDS.max_pension_contribution,
            range_message=(
                f"Employee pension contribution must be between 0.0 and "
                f"{VALIDATION_BOUNDS.max_pension_contribution:g}."
            ),
        ),
        FieldSpec(
            key=InputField.CURRENT_PENSION_POT,
            label="Current pension pot",
            default=INPUT_DEFAULTS.current_pension_pot,
            minimum=0,
            maximum=VALIDATION_BOUNDS.max_current_pension_pot,
            range_message=(
                f"Current pension pot must be between 0 and "
                f"{VALIDATION_BOUNDS.max_current_pension_pot:,.0f}."
            ),
        ),
        FieldSpec(
            key=InputField.SICK_DAYS,
            label="Estimated sick days",
            default=INPUT_DEFAULTS.sick_days,
            minimum=0,
            maximum=VALIDATION_BOUNDS.max_sick_days,
            integer=True,
            range_message=(
                f"Estimated sick days must be between 0 and "
                f"{VALIDATION_BOUNDS.max_sick_days}."
            ),
        ),
        FieldSpec(
            key=InputField.HOLIDAY_DAYS,
            label="Holiday days",
            default=INPUT_DEFAULTS.holiday_days,
            minimum=VALIDATION_BOUNDS.min_holiday_days,
            maximum=VALIDATION_BOUNDS.max_holiday_days,
            integer=True,
            range_message=(
                f"Holiday days must be between "
                f"{VALIDATION_BOUNDS.min_holiday_days} and "
                f"{VALIDATION_BOUNDS.max_holiday_days}."
            ),
        ),
        FieldSpec(
            key=InputField.HOLIDAY_ROLLOVER,
            label="Holiday rollover days",
            default=INPUT_DEFAULTS.holiday_rollover,
            minimum=0,
            maximum=VALIDATION_BOUNDS.max_holiday_rollover,
            integer=True,
            range_message=(
                f"Holiday rollover days must be between 0 and "
                f"{VALIDATION_BOUNDS.max_holiday_rollover}."
            ),
        ),
        FieldSpec(
            key=InputField.HEALTH_INSURANCE_ANNUAL,
            label="Health insurance premium",
            default=0,
            minimum=0,
            maximum=VALIDATION_BOUNDS.max_health_insurance_annual,
            range_message=(
                f"Health insurance premium must be between 0 and "
                f"{VALIDATION_BOUNDS.max_health_insurance_annual:,.0f}."
            ),
        ),
        FieldSpec(
            key=InputField.YEARLY_SPEND,
            label="Yearly spending",
            default=INPUT_DEFAULTS.yearly_spend,
            minimum=VALIDATION_BOUNDS.min_yearly_spend,
            maximum=VALIDATION_BOUNDS.max_yearly_spend,
            range_message=(
                f"Yearly spending must be between "
                f"{VALIDATION_BOUNDS.min_yearly_spend:,.0f} and "
                f"{VALIDATION_BOUNDS.max_yearly_spend:,.0f}."
            ),
        ),
    )

    raw_values = {
        InputField.GROSS_INCOME: gross_income_ui.value,
        InputField.ANNUAL_BONUS: annual_bonus_ui.value,
        InputField.EMPLOYER_PENSION_CONTRIBUTION: employer_pension_contribution_ui.value,
        InputField.EMPLOYEE_PENSION_CONTRIBUTION: employee_pension_contribution_ui.value,
        InputField.CURRENT_PENSION_POT: forecast_current_pension_pot_ui.value,
        InputField.SICK_DAYS: sick_days_ui.value,
        InputField.HOLIDAY_DAYS: holiday_days_ui.value,
        InputField.HOLIDAY_ROLLOVER: holiday_rollover_ui.value,
        InputField.HEALTH_INSURANCE_ANNUAL: health_insurance_annual_ui.value,
        InputField.YEARLY_SPEND: yearly_spend_ui.value,
    }

    parsed_values: dict[InputField, float] = {}
    errors: list[str] = []

    for spec in field_specs:
        raw_value = raw_values[spec.key]
        if raw_value is None:
            errors.append(f"{spec.label} is required.")
            parsed_values[spec.key] = float(spec.default)
            continue

        parsed_value = float(raw_value)
        if spec.integer and not parsed_value.is_integer():
            errors.append(f"{spec.label} must be a whole number.")
            parsed_values[spec.key] = float(spec.default)
            continue

        normalized_value = float(int(parsed_value)) if spec.integer else parsed_value

        in_min = spec.minimum is None or normalized_value >= spec.minimum
        in_max = spec.maximum is None or normalized_value <= spec.maximum
        if not (in_min and in_max):
            errors.append(spec.range_message or f"{spec.label} is out of range.")

        parsed_values[spec.key] = normalized_value

    employer_pension_contribution = parsed_values[
        InputField.EMPLOYER_PENSION_CONTRIBUTION
    ]
    employee_pension_contribution = parsed_values[
        InputField.EMPLOYEE_PENSION_CONTRIBUTION
    ]
    if (
        employer_pension_contribution + employee_pension_contribution
        < TAX_RATES.min_total_pension_contribution
    ):
        errors.append(
            "Employer + employee pension contribution must be at least 0.08 (8%)."
        )

    if errors:
        mo.stop(
            predicate=True,
            output=mo.md(
                "### Input validation errors\n" + "\n".join(f"- {e}" for e in errors)
            ),
        )

    sick_days = int(parsed_values[InputField.SICK_DAYS])
    holiday_days = int(parsed_values[InputField.HOLIDAY_DAYS])
    holiday_rollover = int(parsed_values[InputField.HOLIDAY_ROLLOVER])

    health_insurance_toggle = bool(health_insurance_toggle_ui.value)

    student_loan_flags: dict[StudentLoanPlan, bool] = {
        StudentLoanPlan.PLAN_1: bool(plan_1_ui.value),
        StudentLoanPlan.PLAN_2: bool(plan_2_ui.value),
        StudentLoanPlan.PLAN_4: bool(plan_4_ui.value),
        StudentLoanPlan.PLAN_5: bool(plan_5_ui.value),
        StudentLoanPlan.POSTGRADUATE: bool(postgraduate_ui.value),
    }
    selected_student_loan_plans = tuple(
        plan for plan, enabled in student_loan_flags.items() if enabled
    )

    options = CalcOptions(
        student_loan_plans=selected_student_loan_plans,
        sick_pay_type=SickPayType(sick_pay_type_ui.value),
        sick_days_per_year=sick_days,
        holiday_days=holiday_days + holiday_rollover,
        health_insurance_annual=(
            parsed_values[InputField.HEALTH_INSURANCE_ANNUAL]
            if health_insurance_toggle
            else 0.0
        ),
        health_insurance_bik=(
            parsed_values[InputField.HEALTH_INSURANCE_ANNUAL]
            if health_insurance_toggle
            else 0.0
        ),
    )

    user_inputs = UserInputs(
        gross_income=parsed_values[InputField.GROSS_INCOME],
        annual_bonus=parsed_values[InputField.ANNUAL_BONUS],
        employer_pension_contribution=employer_pension_contribution,
        employee_pension_contribution=employee_pension_contribution,
        current_pension_pot=parsed_values[InputField.CURRENT_PENSION_POT],
        sick_days=sick_days,
        holiday_days=holiday_days,
        holiday_rollover=holiday_rollover,
        health_insurance_annual=parsed_values[InputField.HEALTH_INSURANCE_ANNUAL],
        health_insurance_toggle=health_insurance_toggle,
        yearly_spend=parsed_values[InputField.YEARLY_SPEND],
    )
    return options, user_inputs


@app.cell(hide_code=True)
def _(user_inputs):
    base_monthly_gross = user_inputs.gross_income / 12
    return (base_monthly_gross,)


@app.cell(hide_code=True)
def _(base_monthly_gross, calc_pay_ras, options, user_inputs):
    curr = calc_pay_ras(
        base_monthly_gross,
        user_inputs.employer_pension_contribution,
        user_inputs.employee_pension_contribution,
        options,
    )
    return (curr,)


@app.cell(hide_code=True)
def _(base_monthly_gross, calc_pay_ras, options, user_inputs):
    optimization_curr = calc_pay_ras(
        base_monthly_gross,
        user_inputs.employer_pension_contribution,
        user_inputs.employee_pension_contribution,
        options,
    )
    return (optimization_curr,)


@app.cell(hide_code=True)
def _(INPUT_DEFAULTS, OptimizationTarget, mo):
    objective_options = {
        "Max take-home": OptimizationTarget.TAKE_HOME.value,
        "Max effective net": OptimizationTarget.EFFECTIVE_NET.value,
        "Max forecasted value": OptimizationTarget.FORECASTED_VALUE.value,
    }
    default_objective_label = next(
        label
        for label, objective_value in objective_options.items()
        if objective_value == INPUT_DEFAULTS.optimize_target.value
    )
    optimize_objective_ui = mo.ui.radio(
        options=objective_options,
        value=default_objective_label,
        label="Optimisation target",
    )
    optimize_search_gross_ui = mo.ui.checkbox(
        label="Also search gross salary + employer + employee pension",
        value=INPUT_DEFAULTS.optimize_search_all_three,
    )
    return optimize_objective_ui, optimize_search_gross_ui


@app.cell(hide_code=True)
def _(
    OptimizationTarget,
    forecast_current_pension_pot_ui,
    forecast_drawdown_years_ui,
    forecast_inflation_ui,
    forecast_isa_management_fee_ui,
    forecast_market_apy_ui,
    forecast_pension_amc_ui,
    forecast_terminal_value,
    forecast_years_ui,
    optimize_objective_ui,
    optimization_curr,
    optimize_proposal,
    optimize_search_gross_ui,
    options,
    user_inputs,
):
    _years = max(1, int(float(forecast_years_ui.value or 1)))
    _market_apy = float(forecast_market_apy_ui.value or 0.0)
    _inflation = float(forecast_inflation_ui.value or 0.0)
    _pension_amc = float(forecast_pension_amc_ui.value or 0.0)
    _isa_management_fee = float(forecast_isa_management_fee_ui.value or 0.0)
    _current_pension_pot = float(forecast_current_pension_pot_ui.value or 0.0)
    _drawdown_years = max(1, int(float(forecast_drawdown_years_ui.value or 1)))
    _objective_mode = OptimizationTarget(optimize_objective_ui.value)
    _search_salary_employer_employee = bool(optimize_search_gross_ui.value)
    _objective_cache: dict[tuple[float, float], float] = {}

    def objective_fn(proposal) -> float:
        if _objective_mode == OptimizationTarget.TAKE_HOME:
            return proposal.net_pay
        if _objective_mode == OptimizationTarget.EFFECTIVE_NET:
            return proposal.theoretical_net

        cache_key = (proposal.net_pay, proposal.total_pension_contribution)
        cached_score = _objective_cache.get(cache_key)
        if cached_score is not None:
            return cached_score

        score = forecast_terminal_value(
            net_pay=proposal.net_pay,
            total_pension_contribution=proposal.total_pension_contribution,
            yearly_spend=user_inputs.yearly_spend,
            current_pension_pot=_current_pension_pot,
            drawdown_years=_drawdown_years,
            years=_years,
            market_apy=_market_apy,
            inflation=_inflation,
            pension_amc=_pension_amc,
            isa_management_fee=_isa_management_fee,
        )
        _objective_cache[cache_key] = score
        return score

    optimization = optimize_proposal(
        curr=optimization_curr,
        yearly_spend=user_inputs.yearly_spend,
        options=options,
        objective_fn=objective_fn,
        search_salary_employer_employee=_search_salary_employer_employee,
    )
    return (optimization,)


@app.cell(hide_code=True)
def _(
    OptimizationTarget,
    TAX_RATES,
    VALIDATION_BOUNDS,
    calc_pay_ras,
    forecast_current_pension_pot_ui,
    forecast_drawdown_years_ui,
    forecast_inflation_ui,
    forecast_isa_management_fee_ui,
    forecast_market_apy_ui,
    forecast_pension_amc_ui,
    forecast_terminal_value,
    forecast_years_ui,
    optimize_objective_ui,
    optimize_search_gross_ui,
    options,
    optimization_curr,
    pl,
    user_inputs,
):
    def _frange(start: float, stop: float, step: float) -> tuple[float, ...]:
        span = max(0.0, stop - start)
        steps = round(span / step)
        return tuple(round(start + index * step, 12) for index in range(steps + 1))

    _years = max(1, int(float(forecast_years_ui.value or 1)))
    _market_apy = float(forecast_market_apy_ui.value or 0.0)
    _inflation = float(forecast_inflation_ui.value or 0.0)
    _pension_amc = float(forecast_pension_amc_ui.value or 0.0)
    _isa_management_fee = float(forecast_isa_management_fee_ui.value or 0.0)
    _current_pension_pot = float(forecast_current_pension_pot_ui.value or 0.0)
    _drawdown_years = max(1, int(float(forecast_drawdown_years_ui.value or 1)))
    _objective_mode = OptimizationTarget(optimize_objective_ui.value)
    _search_salary_employer_employee = bool(optimize_search_gross_ui.value)
    _objective_cache: dict[tuple[float, float], float] = {}

    def objective_value(proposal) -> float:
        if _objective_mode == OptimizationTarget.TAKE_HOME:
            return proposal.net_pay
        if _objective_mode == OptimizationTarget.EFFECTIVE_NET:
            return proposal.theoretical_net

        cache_key = (proposal.net_pay, proposal.total_pension_contribution)
        cached_score = _objective_cache.get(cache_key)
        if cached_score is not None:
            return cached_score

        score = forecast_terminal_value(
            net_pay=proposal.net_pay,
            total_pension_contribution=proposal.total_pension_contribution,
            yearly_spend=user_inputs.yearly_spend,
            current_pension_pot=_current_pension_pot,
            drawdown_years=_drawdown_years,
            years=_years,
            market_apy=_market_apy,
            inflation=_inflation,
            pension_amc=_pension_amc,
            isa_management_fee=_isa_management_fee,
        )
        _objective_cache[cache_key] = score
        return score

    current_annual_gross = optimization_curr.inputs.gross * 12
    fixed_employer_rate = optimization_curr.inputs.employer_prc
    if _search_salary_employer_employee:
        gross_floor = max(
            VALIDATION_BOUNDS.min_gross_income,
            current_annual_gross * 0.7,
        )
        gross_ceiling = min(
            VALIDATION_BOUNDS.max_gross_income,
            current_annual_gross * 1.3,
        )
        gross_values = _frange(gross_floor, gross_ceiling, 1_000.0)
        employer_values = _frange(0.0, VALIDATION_BOUNDS.max_pension_contribution, 0.02)
    else:
        gross_values = (current_annual_gross,)
        employer_values = (fixed_employer_rate,)

    sweep_rows: list[dict[str, float]] = []
    surface_rows: list[dict[str, float]] = []

    for employee_rate in _frange(0.0, 0.5, 0.005):
        best_proposal = None
        best_objective = float("-inf")
        for employer_rate in employer_values:
            if employer_rate + employee_rate < TAX_RATES.min_total_pension_contribution:
                continue

            best_pair_proposal = None
            best_pair_objective = float("-inf")
            for annual_gross in gross_values:
                proposal = calc_pay_ras(
                    annual_gross / 12,
                    employer_rate,
                    employee_rate,
                    options,
                )
                if (
                    proposal.employer_total_outgoing
                    > optimization_curr.employer_total_outgoing
                ):
                    break
                if proposal.net_pay * 12 < user_inputs.yearly_spend:
                    continue

                score = objective_value(proposal)
                if best_pair_proposal is None or score > best_pair_objective:
                    best_pair_proposal = proposal
                    best_pair_objective = score
                if best_proposal is None or score > best_objective:
                    best_proposal = proposal
                    best_objective = score

            if best_pair_proposal is None:
                continue

            surface_rows.append(
                {
                    "employee_pension_pct": employee_rate * 100,
                    "employer_pension_pct": employer_rate * 100,
                    "best_gross_annual": best_pair_proposal.annual.gross,
                    "take_home_annual": best_pair_proposal.net_pay * 12,
                    "pension_annual": best_pair_proposal.total_pension_contribution
                    * 12,
                    "effective_net_annual": best_pair_proposal.theoretical_net * 12,
                    "employer_cost_annual": best_pair_proposal.employer_total_outgoing
                    * 12,
                    "yearly_spend_annual": user_inputs.yearly_spend,
                    "projected_total_at_horizon": best_pair_objective,
                }
            )

        if best_proposal is None:
            continue

        sweep_rows.append(
            {
                "employee_pension_pct": employee_rate * 100,
                "best_gross_annual": best_proposal.annual.gross,
                "best_employer_pension_pct": best_proposal.inputs.employer_prc * 100,
                "take_home_annual": best_proposal.net_pay * 12,
                "pension_annual": best_proposal.total_pension_contribution * 12,
                "effective_net_annual": best_proposal.theoretical_net * 12,
                "employer_cost_annual": best_proposal.employer_total_outgoing * 12,
                "yearly_spend_annual": user_inputs.yearly_spend,
                "projected_total_at_horizon": best_objective,
            }
        )

    optimization_curve_df = (
        pl.DataFrame(sweep_rows).sort("employee_pension_pct")
        if sweep_rows
        else pl.DataFrame(
            schema={
                "employee_pension_pct": pl.Float64,
                "best_gross_annual": pl.Float64,
                "best_employer_pension_pct": pl.Float64,
                "take_home_annual": pl.Float64,
                "pension_annual": pl.Float64,
                "effective_net_annual": pl.Float64,
                "employer_cost_annual": pl.Float64,
                "yearly_spend_annual": pl.Float64,
                "projected_total_at_horizon": pl.Float64,
            }
        )
    )
    optimization_surface_df = (
        pl.DataFrame(surface_rows).sort(
            ["employee_pension_pct", "employer_pension_pct"]
        )
        if surface_rows
        else pl.DataFrame(
            schema={
                "employee_pension_pct": pl.Float64,
                "employer_pension_pct": pl.Float64,
                "best_gross_annual": pl.Float64,
                "take_home_annual": pl.Float64,
                "pension_annual": pl.Float64,
                "effective_net_annual": pl.Float64,
                "employer_cost_annual": pl.Float64,
                "yearly_spend_annual": pl.Float64,
                "projected_total_at_horizon": pl.Float64,
            }
        )
    )
    return optimization_curve_df, optimization_surface_df


@app.cell(hide_code=True)
def _(c, curr, mo, p, user_inputs):
    current_breakdown_title = mo.md("### Current Salary Breakdown")
    current_breakdown_content = mo.md(f"""
    With a base gross annual salary of {p(curr.annual.gross)} ({p(curr.inputs.gross)}/month):
    Bonus is excluded from calculations (optimisation + forecast); shown here for reference only.

    | | Monthly | Annual |
    |---|---:|---:|
    | **Gross pay** | {p(curr.inputs.gross)} | {p(curr.annual.gross)} |
    | Flat bonus input (display only) | {p(user_inputs.annual_bonus / 12)} | {p(user_inputs.annual_bonus)} |
    | Income tax | {p(curr.details.tax)} | {p(curr.annual.tax)} |
    | Employee NI | {p(curr.details.national_insurance)} | {p(curr.annual.ni)} |
    | Student loan | {p(curr.details.student_loan)} | {p(curr.annual.student_loan)} |
    | Employee pension ({c(curr.inputs.employee_prc)}) | {p(curr.details.employee_pension_contribution)} | {p(curr.details.employee_pension_contribution * 12)} |
    | SSP deduction | {p(curr.details.ssp_deduction)} | {p(curr.annual.ssp_deduction)} |
    | BIK tax (health ins.) | {p(curr.details.health_insurance_bik_tax)} | {p(curr.details.health_insurance_bik_tax * 12)} |
    | **Net take-home** | **{p(curr.net_pay)}** | **{p(curr.annual.net_pay)}** |
    | Employer pension ({c(curr.inputs.employer_prc)}) | {p(curr.details.employer_pension_contribution)} | {p(curr.details.employer_pension_contribution * 12)} |
    | Gov pension top-up (RAS only) | {p(curr.details.gov_pension_contribution)} | {p(curr.details.gov_pension_contribution * 12)} |
    | **Total pension** | **{p(curr.total_pension_contribution)}** | **{p(curr.total_pension_contribution * 12)}** |
    | **Effective net (pay + pension)** | **{p(curr.theoretical_net)}** | **{p(curr.theoretical_net * 12)}** |
    | **Employer total cost** | {p(curr.employer_total_outgoing)} | {p(curr.annual.employer_total)} |
    """)
    current_breakdown_section = mo.vstack(
        [current_breakdown_title, current_breakdown_content]
    )
    return (current_breakdown_section,)


@app.cell(hide_code=True)
def _(HOURS_PER_WEEK, TAX_RATES, curr, mo, p):
    rates = curr.rates
    rate_line = (
        " - sick days"
        if rates.effective_working_days
        < TAX_RATES.working_days_per_year - rates.holiday_days
        else ""
    )

    rates_title = mo.md("### Effective Rates")
    rates_content = mo.md(
        f"""
        Based on {rates.effective_working_days} working days ({TAX_RATES.working_days_per_year} - {rates.holiday_days} holidays{rate_line}), {TAX_RATES.standard_hours_per_day}h/day and {HOURS_PER_WEEK}h/week:

        | | Net | Gross |
        |---|---:|---:|
        | **Daily** | {p(rates.effective_daily_rate)} | {p(rates.gross_daily_rate)} |
        | **Hourly** | {p(rates.effective_hourly_rate)} | {p(rates.gross_hourly_rate)} |
        | **Weekly** | {p(rates.effective_weekly_rate)} | {p(rates.gross_weekly_rate)} |
        | **Monthly** | {p(rates.effective_monthly_rate)} | {p(rates.gross_monthly_rate)} |
        """
    )
    rates_section = mo.vstack([rates_title, rates_content])
    return (rates_section,)


@app.cell(hide_code=True)
def _(HEALTH_INSURANCE_BENCHMARK, income_tax, mo, p, user_inputs):
    if user_inputs.health_insurance_annual <= 0:
        health_insurance_section = mo.md("")
    else:
        annual_cost = user_inputs.health_insurance_annual
        annual_tax_base = user_inputs.gross_income + user_inputs.annual_bonus
        est_axa_annual = 12 * HEALTH_INSURANCE_BENCHMARK.axa_monthly_estimate
        est_vitality_annual = 12 * HEALTH_INSURANCE_BENCHMARK.vitality_monthly_estimate
        est_blended_annual = 12 * HEALTH_INSURANCE_BENCHMARK.blended_monthly_estimate

        if user_inputs.health_insurance_toggle:
            extra_tax = income_tax(annual_tax_base + annual_cost) - income_tax(
                annual_tax_base
            )
            mode = "Employer Benefits"
            net_personal_cost = extra_tax
            comparison_delta = est_blended_annual - net_personal_cost
            comparison_label = "Estimated personal cost avoided vs blended AXA+Vitality"
        else:
            extra_tax = 0.0
            mode = "Personal Insurance"
            net_personal_cost = annual_cost
            comparison_delta = annual_cost - est_blended_annual
            comparison_label = "Entered personal cost vs blended AXA+Vitality estimate"

        health_insurance_section = mo.md(
            f"""
            ### Health Insurance Analysis ({mode})
            | | Annual | Monthly |
            |---|---:|---:|
            | Entered premium | {p(annual_cost)} | {p(annual_cost / 12)} |
            | BIK tax impact | {p(extra_tax)} | {p(extra_tax / 12)} |
            | Your net personal cost | {p(net_personal_cost)} | {p(net_personal_cost / 12)} |
            | AXA benchmark estimate | {p(est_axa_annual)} | {p(est_axa_annual / 12)} |
            | Vitality estimate (official 'from') | {p(est_vitality_annual)} | {p(est_vitality_annual / 12)} |
            | Blended AXA+Vitality estimate | {p(est_blended_annual)} | {p(est_blended_annual / 12)} |
            | {comparison_label} | {p(comparison_delta)} | {p(comparison_delta / 12)} |

            Sources (checked {HEALTH_INSURANCE_BENCHMARK.as_of}):
            - Vitality: {HEALTH_INSURANCE_BENCHMARK.vitality_source}
            - AXA product page: {HEALTH_INSURANCE_BENCHMARK.axa_source}
            - AXA benchmark source: {HEALTH_INSURANCE_BENCHMARK.axa_benchmark_source}
            """
        )
    return (health_insurance_section,)


@app.cell(hide_code=True)
def _(
    OptimizationTarget,
    alt,
    c,
    forecast_years_ui,
    mo,
    optimize_objective_ui,
    optimize_search_gross_ui,
    optimization,
    optimization_curr,
    optimization_curve_df,
    optimization_surface_df,
    pl,
    user_inputs,
):
    _objective_mode = OptimizationTarget(optimize_objective_ui.value)
    _objective_label = {
        OptimizationTarget.TAKE_HOME: "Max take-home",
        OptimizationTarget.EFFECTIVE_NET: "Max effective net",
        OptimizationTarget.FORECASTED_VALUE: "Max forecasted value",
    }.get(_objective_mode, "Max forecasted value")
    _search_label = (
        "Searching gross salary + employer + employee pension."
        if optimize_search_gross_ui.value
        else "Searching employee pension only (gross salary and employer pension fixed)."
    )
    _objective_suffix = (
        f" at year {int(float(forecast_years_ui.value or 1))}"
        if _objective_mode == OptimizationTarget.FORECASTED_VALUE
        else ""
    )

    if optimization.result is None:
        summary = mo.md(f"*{optimization.reason}*")
    else:
        optimization_result = optimization.result
        summary = mo.md(
            f"""
            ### Optimised Proposal
            Optimisation target: **{_objective_label}{_objective_suffix}**.
            {_search_label}

            Best proposal: base gross salary {optimization_result.annual.gross:,.0f}/year, employer contribution {c(optimization_result.inputs.employer_prc)}, employee contribution {c(optimization_result.inputs.employee_prc)}.
            """
        )

    optimization_controls = mo.hstack(
        [optimize_objective_ui, optimize_search_gross_ui],
        align="start",
    )

    _is_surface_mode = bool(optimize_search_gross_ui.value)
    _plot_explainer = (
        mo.md(
            "Surface view: each point is an employee/employer pension mix, colored by optimisation objective, with gross salary shown in the second chart."
        )
        if _is_surface_mode
        else mo.md(
            "Curve view: each point is the best proposal for an employee pension contribution."
        )
    )
    _has_data = (
        not optimization_surface_df.is_empty()
        if _is_surface_mode
        else not optimization_curve_df.is_empty()
    )

    if not _has_data:
        comparison_table = mo.md("*No comparison range available for current inputs.*")
    elif _is_surface_mode:
        comparison_table_df = (
            optimization_surface_df.sort("projected_total_at_horizon", descending=True)
            .head(40)
            .select(
                pl.col("employee_pension_pct")
                .round(2)
                .alias("Employee contribution (%)"),
                pl.col("employer_pension_pct")
                .round(2)
                .alias("Employer contribution (%)"),
                pl.col("best_gross_annual").round(2).alias("Best gross salary (£/yr)"),
                pl.col("take_home_annual").round(2).alias("Take-home (£/yr)"),
                pl.col("pension_annual").round(2).alias("Pension (£/yr)"),
                pl.col("effective_net_annual").round(2).alias("Effective net (£/yr)"),
                pl.col("employer_cost_annual").round(2).alias("Employer cost (£/yr)"),
                pl.col("projected_total_at_horizon")
                .round(2)
                .alias("Objective value (£)"),
            )
        )
        comparison_table = mo.ui.table(comparison_table_df, page_size=12)
    else:
        comparison_table_df = optimization_curve_df.select(
            pl.col("employee_pension_pct").round(2).alias("Employee contribution (%)"),
            pl.col("best_gross_annual").round(2).alias("Best gross salary (£/yr)"),
            pl.col("best_employer_pension_pct")
            .round(2)
            .alias("Employer contribution (%)"),
            pl.col("take_home_annual").round(2).alias("Take-home (£/yr)"),
            pl.col("pension_annual").round(2).alias("Pension (£/yr)"),
            pl.col("effective_net_annual").round(2).alias("Effective net (£/yr)"),
            pl.col("employer_cost_annual").round(2).alias("Employer cost (£/yr)"),
        )
        comparison_table = mo.ui.table(comparison_table_df, page_size=10)

    if not _has_data:
        chart_block = mo.md(
            "*No feasible optimisation curve to plot for current inputs.*"
        )
        changes_block = mo.md("")
    elif _is_surface_mode:
        current_mix_point = (
            alt.Chart(
                pl.DataFrame(
                    {
                        "employee_pension_pct": [
                            optimization_curr.inputs.employee_prc * 100
                        ],
                        "employer_pension_pct": [
                            optimization_curr.inputs.employer_prc * 100
                        ],
                    }
                )
            )
            .mark_point(
                shape="diamond",
                color="white",
                stroke="#222222",
                strokeWidth=1.5,
                size=140,
            )
            .encode(
                x="employee_pension_pct:Q",
                y="employer_pension_pct:Q",
            )
        )

        objective_surface_chart = (
            alt.Chart(optimization_surface_df)
            .mark_rect()
            .encode(
                x=alt.X(
                    "employee_pension_pct:Q",
                    title="Employee pension contribution (%)",
                ),
                y=alt.Y(
                    "employer_pension_pct:Q",
                    title="Employer pension contribution (%)",
                ),
                color=alt.Color(
                    "projected_total_at_horizon:Q",
                    title=f"{_objective_label}{_objective_suffix} (£)",
                ),
                tooltip=[
                    alt.Tooltip(
                        "employee_pension_pct:Q", title="Employee %", format=".2f"
                    ),
                    alt.Tooltip(
                        "employer_pension_pct:Q", title="Employer %", format=".2f"
                    ),
                    alt.Tooltip(
                        "best_gross_annual:Q", title="Best gross (£/yr)", format=",.2f"
                    ),
                    alt.Tooltip(
                        "take_home_annual:Q", title="Take-home (£/yr)", format=",.2f"
                    ),
                    alt.Tooltip(
                        "pension_annual:Q", title="Pension (£/yr)", format=",.2f"
                    ),
                    alt.Tooltip(
                        "effective_net_annual:Q",
                        title="Effective net (£/yr)",
                        format=",.2f",
                    ),
                    alt.Tooltip(
                        "employer_cost_annual:Q",
                        title="Employer cost (£/yr)",
                        format=",.2f",
                    ),
                    alt.Tooltip(
                        "projected_total_at_horizon:Q",
                        title="Objective (£)",
                        format=",.2f",
                    ),
                ],
            )
            .properties(width=840, height=360)
        )
        chart_block = mo.ui.altair_chart(objective_surface_chart + current_mix_point)

        gross_surface_chart = (
            alt.Chart(optimization_surface_df)
            .mark_circle(opacity=0.85)
            .encode(
                x=alt.X(
                    "employee_pension_pct:Q",
                    title="Employee pension contribution (%)",
                ),
                y=alt.Y(
                    "employer_pension_pct:Q",
                    title="Employer pension contribution (%)",
                ),
                color=alt.Color(
                    "best_gross_annual:Q", title="Best gross salary (£/yr)"
                ),
                size=alt.Size("projected_total_at_horizon:Q", title="Objective score"),
                tooltip=[
                    alt.Tooltip(
                        "employee_pension_pct:Q", title="Employee %", format=".2f"
                    ),
                    alt.Tooltip(
                        "employer_pension_pct:Q", title="Employer %", format=".2f"
                    ),
                    alt.Tooltip(
                        "best_gross_annual:Q", title="Best gross (£/yr)", format=",.2f"
                    ),
                    alt.Tooltip(
                        "projected_total_at_horizon:Q",
                        title="Objective (£)",
                        format=",.2f",
                    ),
                ],
            )
            .properties(width=840, height=320)
        )
        changes_block = mo.ui.altair_chart(gross_surface_chart + current_mix_point)
    else:
        active_series: list[tuple[str, str]] = [
            ("Take-home", "take_home_annual"),
            ("Pension", "pension_annual"),
            ("Approximate Yearly Spending", "yearly_spend_annual"),
            ("Effective net", "effective_net_annual"),
            ("Employer cost", "employer_cost_annual"),
        ]

        long_frames = [
            optimization_curve_df.select(
                "employee_pension_pct",
                pl.col(column_name).alias("amount"),
            ).with_columns(pl.lit(series_name).alias("series"))
            for series_name, column_name in active_series
        ]
        long_df = pl.concat(long_frames, how="vertical")

        line_chart = (
            alt.Chart(long_df)
            .mark_line(strokeWidth=2)
            .encode(
                x=alt.X(
                    "employee_pension_pct:Q",
                    title="Employee pension contribution (%)",
                ),
                y=alt.Y("amount:Q", title="Annual value (£)"),
                color=alt.Color("series:N", title="Lines"),
                tooltip=[
                    alt.Tooltip("series:N", title="Series"),
                    alt.Tooltip(
                        "employee_pension_pct:Q",
                        title="Employee %",
                        format=".2f",
                    ),
                    alt.Tooltip("amount:Q", title="Annual £", format=",.2f"),
                ],
            )
            .properties(width=840, height=420)
        )

        current_rate_rule = (
            alt.Chart(
                pl.DataFrame(
                    {
                        "employee_pension_pct": [
                            optimization_curr.inputs.employee_prc * 100
                        ]
                    }
                )
            )
            .mark_rule(color="#555555", strokeDash=[4, 4], strokeWidth=1.5)
            .encode(x="employee_pension_pct:Q")
        )

        chart_block = mo.ui.altair_chart(line_chart + current_rate_rule)

        delta_columns = [
            ("Take-home delta", "take_home_annual", optimization_curr.net_pay * 12),
            (
                "Pension delta",
                "pension_annual",
                optimization_curr.total_pension_contribution * 12,
            ),
            (
                "Effective net delta",
                "effective_net_annual",
                optimization_curr.theoretical_net * 12,
            ),
            (
                "Employer cost delta",
                "employer_cost_annual",
                optimization_curr.employer_total_outgoing * 12,
            ),
        ]

        delta_frames = [
            optimization_curve_df.select(
                "employee_pension_pct",
                (pl.col(column_name) - baseline).alias("delta_amount"),
            ).with_columns(pl.lit(series_name).alias("series"))
            for series_name, column_name, baseline in delta_columns
        ]
        deltas_df = pl.concat(delta_frames, how="vertical")

        delta_chart = (
            alt.Chart(deltas_df)
            .mark_line(strokeWidth=2)
            .encode(
                x=alt.X(
                    "employee_pension_pct:Q",
                    title="Employee pension contribution (%)",
                ),
                y=alt.Y("delta_amount:Q", title="Annual change vs current (£)"),
                color=alt.Color("series:N", title="Delta lines"),
                tooltip=[
                    alt.Tooltip("series:N", title="Series"),
                    alt.Tooltip(
                        "employee_pension_pct:Q",
                        title="Employee %",
                        format=".2f",
                    ),
                    alt.Tooltip(
                        "delta_amount:Q", title="Annual delta £", format=",.2f"
                    ),
                ],
            )
            .properties(width=840, height=320)
        )
        zero_rule = (
            alt.Chart(pl.DataFrame({"zero": [0.0]}))
            .mark_rule(color="#888888")
            .encode(y="zero:Q")
        )
        changes_block = mo.ui.altair_chart(delta_chart + zero_rule)

    graphs_stack = mo.vstack([chart_block, changes_block])
    merged_layout = mo.vstack([graphs_stack, comparison_table])

    optimization_section = mo.vstack(
        [
            summary,
            optimization_controls,
            _plot_explainer,
            mo.md(
                f"Constraints used: employer cost must stay at or below current package (excluding flat bonus) and net take-home must stay at or above yearly spending ({user_inputs.yearly_spend:,.0f})."
            ),
            merged_layout,
        ]
    )
    return (optimization_section,)


@app.cell(hide_code=True)
def _(curr, mo, optimization, p):
    if optimization.result is None:
        comparison_section = mo.md("")
    else:
        comparison_result = optimization.result
        comparison_section = mo.md(
            f"""
            ### Comparison (Optimised vs Current)
            | | Monthly | Annual |
            |---|---:|---:|
            | Effective net change | {p(comparison_result.theoretical_net - curr.theoretical_net)} | {p(12 * (comparison_result.theoretical_net - curr.theoretical_net))} |
            | Take-home change | {p(comparison_result.net_pay - curr.net_pay)} | {p(12 * (comparison_result.net_pay - curr.net_pay))} |
            | Pension change | {p(comparison_result.total_pension_contribution - curr.total_pension_contribution)} | {p(12 * (comparison_result.total_pension_contribution - curr.total_pension_contribution))} |
            | Employer cost change | {p(comparison_result.employer_total_outgoing - curr.employer_total_outgoing)} | {p(12 * (comparison_result.employer_total_outgoing - curr.employer_total_outgoing))} |
            """
        )
    return (comparison_section,)


@app.cell(hide_code=True)
def _(INPUT_DEFAULTS, mo):
    forecast_use_optimized_ui = mo.ui.checkbox(
        label="Show optimised forecast alongside current",
        value=INPUT_DEFAULTS.forecast_use_optimized,
    )
    return (forecast_use_optimized_ui,)


@app.cell(hide_code=True)
def _(
    alt,
    forecast_drawdown_years_ui,
    forecast_inflation_ui,
    forecast_isa_management_fee_ui,
    forecast_market_apy_ui,
    forecast_pension_amc_ui,
    forecast_projection,
    forecast_use_optimized_ui,
    forecast_years_ui,
    mo,
    optimization,
    optimization_curr,
    pl,
    user_inputs,
):
    years = max(1, int(float(forecast_years_ui.value or 1)))
    market_apy = float(forecast_market_apy_ui.value or 0.0)
    inflation = float(forecast_inflation_ui.value or 0.0)
    pension_amc = float(forecast_pension_amc_ui.value or 0.0)
    isa_management_fee = float(forecast_isa_management_fee_ui.value or 0.0)
    drawdown_years = max(1, int(float(forecast_drawdown_years_ui.value or 1)))
    compare_with_optimized = bool(forecast_use_optimized_ui.value)
    has_optimized = optimization.result is not None

    current_rows = forecast_projection(
        net_pay=optimization_curr.net_pay,
        total_pension_contribution=optimization_curr.total_pension_contribution,
        yearly_spend=user_inputs.yearly_spend,
        current_pension_pot=user_inputs.current_pension_pot,
        drawdown_years=drawdown_years,
        years=years,
        market_apy=market_apy,
        inflation=inflation,
        pension_amc=pension_amc,
        isa_management_fee=isa_management_fee,
    )
    current_df = pl.DataFrame(current_rows)

    optimized_df = None
    if compare_with_optimized and has_optimized:
        optimized_rows = forecast_projection(
            net_pay=optimization.result.net_pay,
            total_pension_contribution=optimization.result.total_pension_contribution,
            yearly_spend=user_inputs.yearly_spend,
            current_pension_pot=user_inputs.current_pension_pot,
            drawdown_years=drawdown_years,
            years=years,
            market_apy=market_apy,
            inflation=inflation,
            pension_amc=pension_amc,
            isa_management_fee=isa_management_fee,
        )
        optimized_df = pl.DataFrame(optimized_rows)

    chart_frames = [
        current_df.select("year", pl.col("pension_net").alias("amount")).with_columns(
            pl.lit("Current - Pension + growth").alias("series")
        ),
        current_df.select("year", pl.col("isa_net").alias("amount")).with_columns(
            pl.lit("Current - ISA + growth").alias("series")
        ),
        current_df.select("year", pl.col("total_net").alias("amount")).with_columns(
            pl.lit("Current - ISA + pension total").alias("series")
        ),
    ]
    if optimized_df is not None:
        chart_frames.extend(
            [
                optimized_df.select(
                    "year", pl.col("pension_net").alias("amount")
                ).with_columns(pl.lit("Optimised - Pension + growth").alias("series")),
                optimized_df.select(
                    "year", pl.col("isa_net").alias("amount")
                ).with_columns(pl.lit("Optimised - ISA + growth").alias("series")),
                optimized_df.select(
                    "year", pl.col("total_net").alias("amount")
                ).with_columns(
                    pl.lit("Optimised - ISA + pension total").alias("series")
                ),
            ]
        )
    chart_df = pl.concat(chart_frames, how="vertical")

    forecast_chart = (
        alt.Chart(chart_df)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("year:Q", title="Projection year"),
            y=alt.Y("amount:Q", title="Projected value (£)"),
            color=alt.Color("series:N", title="Series"),
            tooltip=[
                alt.Tooltip("series:N", title="Series"),
                alt.Tooltip("year:Q", title="Year", format=".0f"),
                alt.Tooltip("amount:Q", title="Value (£)", format=",.2f"),
            ],
        )
        .properties(height=320)
    )

    if optimized_df is None:
        forecast_table = current_df.select(
            pl.col("year").cast(pl.Int64).alias("Year"),
            pl.col("pension_net").round(2).alias("Current Pension + growth (£)"),
            pl.col("isa_net").round(2).alias("Current ISA + growth (£)"),
            pl.col("total_net").round(2).alias("Current ISA + pension total (£)"),
        )
    else:
        forecast_table = current_df.select(
            pl.col("year").cast(pl.Int64).alias("Year"),
            pl.col("pension_net").round(2).alias("Current Pension + growth (£)"),
            pl.col("isa_net").round(2).alias("Current ISA + growth (£)"),
            pl.col("total_net").round(2).alias("Current ISA + pension total (£)"),
        ).with_columns(
            optimized_df["pension_net"]
            .round(2)
            .alias("Optimised Pension + growth (£)"),
            optimized_df["isa_net"].round(2).alias("Optimised ISA + growth (£)"),
            optimized_df["total_net"]
            .round(2)
            .alias("Optimised ISA + pension total (£)"),
        )

    warning = (
        mo.md(
            "*Current net take-home is below yearly spending, so current ISA/SIPP contributions are zero (pension contributions still continue).*"
        )
        if optimization_curr.net_pay * 12 < user_inputs.yearly_spend
        else mo.md("")
    )
    optimized_warning = (
        mo.md(
            "*Optimised net take-home is below yearly spending, so optimised ISA/SIPP contributions are zero (pension contributions still continue).*"
        )
        if optimized_df is not None
        and optimization.result is not None
        and optimization.result.net_pay * 12 < user_inputs.yearly_spend
        else mo.md("")
    )
    fallback_note = (
        mo.md("*Optimised proposal is unavailable; showing current forecast only.*")
        if compare_with_optimized and not has_optimized
        else mo.md("")
    )
    forecast_explainer = mo.md(
        """
        This chart shows projected value through time in today's terms.
        Lines show pension + growth, ISA + growth, and their total; when enabled, both current and optimised paths are shown.
        Forecast and optimisation exclude the flat bonus by design; bonus is shown in current breakdown only.
        The table lists the same values year-by-year for easier comparison.
        """
    )
    forecast_sanity_check = mo.md(
        f"""
        **Sanity check (base-only):**
        - Base gross: {user_inputs.gross_income:,.0f}
        - Bonus (ignored in calc): {user_inputs.annual_bonus:,.0f}
        - Current net (base-only): {optimization_curr.net_pay * 12:,.0f}/yr
        - Optimised net (base-only): {(optimization.result.net_pay * 12 if optimization.result else 0):,.0f}/yr
        """
    )

    forecast_section = mo.vstack(
        [
            mo.md("### Future Forecast Projection"),
            forecast_use_optimized_ui,
            forecast_explainer,
            forecast_sanity_check,
            fallback_note,
            warning,
            optimized_warning,
            mo.ui.altair_chart(forecast_chart),
            mo.md("### Forecast Data"),
            mo.ui.table(forecast_table),
        ]
    )
    return (forecast_section,)


if __name__ == "__main__":
    app.run()
