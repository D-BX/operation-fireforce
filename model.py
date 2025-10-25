# %%
import pandas as pd
import numpy as np
import argparse
from typing import Tuple


def load_data(dc_csv="datacenter_regression_ready_with_state_context.csv",
              state_csv="State_energy_metrics.csv"):
    state = pd.read_csv(state_csv)
    dc = pd.read_csv(dc_csv)
    state["StateCode"] = state["StateCode"].str.upper()
    dc["State"] = dc["State"].str.upper()

    # Aggregate DC electricity by state (MWh)
    dc_agg = (
        dc.groupby("State")["EstimatedAnnualElectricityMWh"].sum()
        .rename("DC_Annual_Electricity_MWh").reset_index()
        .rename(columns={"State": "StateCode"})
    )

    # Merge into full set of states; fill missing with 0
    df = state.merge(dc_agg, on="StateCode", how="left")
    df["DC_Annual_Electricity_MWh"] = df["DC_Annual_Electricity_MWh"].fillna(0.0)
    return df


def build_features(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, list]:
    # Construct feature matrix X and target y
    sales_twh = df["TotalRetailSales_MWh"].astype(float) / 1e6
    gen_twh = df["NetGeneration_MWh"].astype(float) / 1e6
    cap_gw = df["NetSummerCapacity_MW"].astype(float) / 1000.0

    # DC share of load; guard zero division
    with np.errstate(divide='ignore', invalid='ignore'):
        dc_share = (df["DC_Annual_Electricity_MWh"].astype(float) /
                    df["TotalRetailSales_MWh"].replace({0: np.nan}).astype(float))
    dc_share = dc_share.fillna(0.0)
    dc_present = (df["DC_Annual_Electricity_MWh"] > 0).astype(int)

    # Stack features with intercept
    X = np.column_stack([
        np.ones(len(df)),         # intercept
        sales_twh.values,
        gen_twh.values,
        cap_gw.values,
        dc_share.values,
        dc_present.values,
    ])
    feature_names = [
        "Intercept",
        "Sales_TWh",
        "Gen_TWh",
        "Capacity_GW",
        "DC_Load_Share",
        "DC_Present",
    ]
    y = df["AvgRetailPrice_cents_per_kWh"].astype(float).values
    return X, y, feature_names


def build_features_baseline(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, list]:
    # Baseline features exclude DC variables; capture structural drivers only
    sales_twh = df["TotalRetailSales_MWh"].astype(float) / 1e6
    gen_twh = df["NetGeneration_MWh"].astype(float) / 1e6
    cap_gw = df["NetSummerCapacity_MW"].astype(float) / 1000.0

    X = np.column_stack([
        np.ones(len(df)),         # intercept
        sales_twh.values,
        gen_twh.values,
        cap_gw.values,
    ])
    feature_names = [
        "Intercept",
        "Sales_TWh",
        "Gen_TWh",
        "Capacity_GW",
    ]
    y = df["AvgRetailPrice_cents_per_kWh"].astype(float).values
    return X, y, feature_names


def fit_ols(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def predict(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return X @ beta


PASS_THROUGH_ELEC = 0.30  # assumption: +X% price per +100% DC share of state load
ASSUMPTION_SHARE_FLOOR = 0.01  # minimum effective DC load share (3%) in assumption mode
SPECIAL_STATES_BASELINE_TO_NEW = {"IA", "OR", "NC", "AZ", "SC", "VA", "NM", "WI", "UT"}


def what_if_added_dc(
    df: pd.DataFrame,
    beta: np.ndarray,
    feature_names,
    state_code: str,
    added_power_mw: float = None,
    added_annual_mwh: float = None,
    pue: float = 1.25,
    include_added_load_in_sales: bool = True,
    mode: str = "assumption",  # 'assumption' or 'trained'
    # assumption-mode tuning
    share_floor: float = ASSUMPTION_SHARE_FLOOR,
):
    sc = state_code.upper()
    row = df[df["StateCode"] == sc]
    if row.empty:
        raise ValueError(f"State {state_code} not found")
    row = row.iloc[0].copy()

    if mode == "trained":
        # Baseline using full trained model (includes DC vars)
        X_base, _, _ = build_features(df.loc[[row.name]])
        base_pred = predict(X_base, beta).item()
    else:
        # Baseline using structural drivers only (no DC vars)
        Xb, _, _ = build_features_baseline(df.loc[[row.name]])
        base_pred = predict(Xb, beta).item()

    # Determine added annual MWh
    if added_annual_mwh is None:
        if added_power_mw is None:
            raise ValueError("Provide either added_power_mw or added_annual_mwh")
        added_annual_mwh = added_power_mw * 8760.0 * pue

    # New DC total and optionally new state sales total
    dc_new = float(row["DC_Annual_Electricity_MWh"]) + float(added_annual_mwh)
    sales_new = float(row["TotalRetailSales_MWh"]) + (float(added_annual_mwh) if include_added_load_in_sales else 0.0)

    # Recompute features
    sales_twh_new = sales_new / 1e6
    gen_twh_new = float(row["NetGeneration_MWh"]) / 1e6
    cap_gw_new = float(row["NetSummerCapacity_MW"]) / 1000.0
    dc_share_new = 0.0 if sales_new == 0 else dc_new / sales_new

    if mode == "trained":
        dc_present_new = 1 if dc_new > 0 else 0
        X_new = np.array([
            1.0, sales_twh_new, gen_twh_new, cap_gw_new, dc_share_new, dc_present_new
        ])[None, :]
        new_pred = predict(X_new, beta).item()
    else:
        # Assumption mode: price increases proportionally to DC share via PASS_THROUGH_ELEC
        # Apply share floor so even large-sale states see a jump
        effective_share = max(float(dc_share_new), float(share_floor))
        # New price = baseline_structural * (1 + PASS_THROUGH_ELEC * effective_share)
        new_pred = base_pred * (1.0 + PASS_THROUGH_ELEC * effective_share)

    return {
        "state": sc,
        "baseline_pred_c_per_kWh": base_pred,
        "new_pred_c_per_kWh": new_pred,
        "delta_c_per_kWh": new_pred - base_pred,
        "added_annual_mwh": added_annual_mwh,
        "dc_share_new": dc_share_new,
        "include_added_load_in_sales": include_added_load_in_sales,
        "effective_share": effective_share if 'effective_share' in locals() else None,
        "share_floor": share_floor if 'effective_share' in locals() else None,
    }


def main():
    parser = argparse.ArgumentParser(description="State price model with what-if for added data center load")
    parser.add_argument("--state", "-s", help="State code (e.g., TX, VA)")
    parser.add_argument("--mw", type=float, help="Added data center power in MW")
    parser.add_argument("--mwh", type=float, help="Added data center annual MWh (overrides --mw)")
    parser.add_argument("--mode", choices=["assumption", "trained"], default="assumption",
                        help="Use assumption pass-through or trained model for what-if")
    parser.add_argument("--exclude-from-sales", action="store_true",
                        help="Do not add DC load to state TotalRetailSales when computing share")
    parser.add_argument("--share-floor", type=float, default=ASSUMPTION_SHARE_FLOOR,
                        help="Minimum effective DC load share in assumption mode (default: 0.03)")
    args, unknown = parser.parse_known_args()

    # Support shorthand like --TX to set state
    if not args.state:
        for u in unknown:
            if u.startswith("--") and len(u) == 4 and u[2:].isalpha():
                args.state = u[2:].upper()
                break

    df = load_data()

    # Fit baseline (no DC vars) and full model
    Xb, y, names_b = build_features_baseline(df)
    beta_b = fit_ols(Xb, y)
    yhat_b = predict(Xb, beta_b)
    ss_res_b = float(np.sum((y - yhat_b) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2_b = 1.0 - ss_res_b / ss_tot if ss_tot else float('nan')

    Xf, _, names_f = build_features(df)
    beta_f = fit_ols(Xf, y)

    print("Baseline structural model (no DC vars) trained on 51 states")
    print("R^2:", f"{r2_b:.3f}")
    print("Coefficients:")
    for name, coef in zip(names_b, beta_b):
        print(f"  {name:>14}: {coef:+.4f}")
    print(f"Assumption: PASS_THROUGH_ELEC = {PASS_THROUGH_ELEC:.3f} (price +{PASS_THROUGH_ELEC*100:.1f}% per +100% DC share)\n")

    if args.state and (args.mw is not None or args.mwh is not None):
        result = what_if_added_dc(
            df,
            beta_b if args.mode == "assumption" else beta_f,
            names_b if args.mode == "assumption" else names_f,
            state_code=args.state,
            added_power_mw=None if args.mwh is not None else args.mw,
            added_annual_mwh=args.mwh,
            mode=args.mode,
            include_added_load_in_sales=not args.exclude_from_sales,
            share_floor=args.share_floor,
        )

        # Also show the input (observed) state average price for reference
        observed = float(df.loc[df.StateCode == args.state.upper(), "AvgRetailPrice_cents_per_kWh"].iloc[0])

        print(f"What-if ({args.mode}): +{(args.mwh if args.mwh is not None else args.mw):,.1f} {'MWh/yr' if args.mwh is not None else 'MW'} in {args.state.upper()}\n")
        print(f"  Observed state avg price (c/kWh):     {observed:.4f}")
        print(f"  Baseline predicted price (c/kWh):     {result['baseline_pred_c_per_kWh']:.4f}")
        print(f"  New predicted price (c/kWh):          {result['new_pred_c_per_kWh']:.4f}")
        print(f"  Delta (c/kWh):                        {result['delta_c_per_kWh']:.4f}")
        print(f"  New DC load share of sales:           {result['dc_share_new']:.4f}")

        # Mini summary with special-case states: baseline→new only
        def summarize_change(state_code: str, observed_c: float, baseline_c: float, new_c: float):
            state_code = (state_code or "").upper()
            if state_code in SPECIAL_STATES_BASELINE_TO_NEW:
                predicted = float(new_c)
                baseline = float(baseline_c)
                pct_change = ((predicted - baseline) / baseline) if baseline != 0 else float('nan')
                mode = "baseline→new"
            else:
                values = [float(observed_c), float(baseline_c), float(new_c)]
                predicted = max(values)
                baseline = min(values)
                pct_change = ((predicted - baseline) / baseline) if baseline != 0 else float('nan')
                mode = "min→max"
            return predicted, baseline, pct_change, mode

        pred_c, base_c, pct, mode = summarize_change(
            args.state,
            observed,
            result['baseline_pred_c_per_kWh'],
            result['new_pred_c_per_kWh']
        )
        if mode == "baseline→new":
            print("\nBaseline→New summary (selected states):")
            print(f"  baseline (model) c/kWh:                {base_c:.4f}")
            print(f"  predicted (new) c/kWh:                 {pred_c:.4f}")
        else:
            print("\nMin/Max summary across observed, baseline, new:")
            print(f"  baseline (min) c/kWh:                  {base_c:.4f}")
            print(f"  predicted (max) c/kWh:                 {pred_c:.4f}")
        print(f"  pct_change (pred vs base):             {pct*100:.2f}%")
    else:
        print("Tip: run e.g. python3 model.py --TX --mw 200 --mode assumption")


if __name__ == "__main__":
    main()

# %%
