import pandas as pd


def process_files(product_df, purchase_df, group_field='Category'):
    # Normalize product column names to match app-side behavior.
    product_df.columns = (
        product_df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "", regex=False)
        .str.replace("_", "", regex=False)
    )

    if len(product_df.columns) < 3:
        raise ValueError("Product coding file must contain at least 3 columns.")

    product_df = product_df.rename(
        columns={
            product_df.columns[0]: 'imageid',
            product_df.columns[1]: 'unitsvariable',
            product_df.columns[2]: 'dollarsvariable',
        }
    )

    group_col = str(group_field).strip().lower().replace(" ", "").replace("_", "")
    if group_col not in product_df.columns:
        raise ValueError(f"Group field '{group_field}' was not found in the product coding file.")

    id_cols = ['record', 'uuid']
    missing_id_cols = [col for col in id_cols if col not in purchase_df.columns]
    if missing_id_cols:
        raise ValueError(f"Missing required purchase columns: {missing_id_cols}")

    mapping = product_df[['unitsvariable', 'dollarsvariable', group_col]].dropna(subset=[group_col]).copy()
    mapping[group_col] = mapping[group_col].astype(str).str.strip()

    result = purchase_df[id_cols].copy()

    # Aggregate directly across mapped columns per group to avoid huge long-format melts.
    for group_value, group_map in mapping.groupby(group_col, sort=False):
        unit_cols = [col for col in group_map['unitsvariable'].dropna().astype(str).tolist() if col in purchase_df.columns]
        dollar_cols = [col for col in group_map['dollarsvariable'].dropna().astype(str).tolist() if col in purchase_df.columns]

        if unit_cols:
            unit_cols = list(dict.fromkeys(unit_cols))
            result[f"Units_{group_value}"] = purchase_df[unit_cols].sum(axis=1, min_count=1)

        if dollar_cols:
            dollar_cols = list(dict.fromkeys(dollar_cols))
            result[f"Dollars_{group_value}"] = purchase_df[dollar_cols].sum(axis=1, min_count=1)

    return result
