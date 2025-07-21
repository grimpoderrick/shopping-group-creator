import pandas as pd

def process_files(product_df, purchase_df, group_field='Category'):
    # Normalize column names in product_df
    product_df.columns = (
        product_df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "")
            .str.replace("_", "")
    )

    # Rename key columns
    product_df = product_df.rename(columns={
        product_df.columns[0]: 'imageid',
        product_df.columns[1]: 'unitsvariable',
        product_df.columns[2]: 'dollarsvariable'
    })

    coding_map = product_df.set_index('imageid')[['unitsvariable', 'dollarsvariable', group_field.lower()]]

    id_cols = ['record', 'uuid']
    group_col = group_field.lower()

    # Process Units
    unit_data = purchase_df[id_cols + coding_map['unitsvariable'].tolist()]
    units_long = unit_data.melt(id_vars=id_cols, var_name='unitsvariable', value_name='Units')
    units_long = units_long.merge(
        coding_map.reset_index()[['unitsvariable', group_col]],
        on='unitsvariable', how='left'
    )

    # Group and aggregate units correctly (null if all values null)
    units_agg = (
        units_long
        .groupby(id_cols + [group_col], as_index=False)
        .agg({'Units': lambda x: x.sum(min_count=1)})
    )

    # Process Dollars
    dollar_data = purchase_df[id_cols + coding_map['dollarsvariable'].tolist()]
    dollars_long = dollar_data.melt(id_vars=id_cols, var_name='dollarsvariable', value_name='Dollars')
    dollars_long = dollars_long.merge(
        coding_map.reset_index()[['dollarsvariable', group_col]],
        on='dollarsvariable', how='left'
    )

    dollars_agg = (
        dollars_long
        .groupby(id_cols + [group_col], as_index=False)
        .agg({'Dollars': lambda x: x.sum(min_count=1)})
    )

    # Combine Units and Dollars
    summary = pd.merge(units_agg, dollars_agg, on=id_cols + [group_col], how='outer')

    # Pivot to wide format while keeping record + uuid
    pivot = summary.pivot(index=id_cols, columns=group_col, values=['Units', 'Dollars'])
    pivot.columns = [f"{metric}_{label}" for metric, label in pivot.columns]
    pivot = pivot.reset_index()

    # Ensure original order is maintained based on appearance in purchase_df
    pivot['__order'] = pivot['record'].map({rec: i for i, rec in enumerate(purchase_df['record'])})
    pivot = pivot.sort_values('__order').drop(columns='__order')

    return pivot
