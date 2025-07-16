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

    # Rename first three columns based on expected structure
    product_df = product_df.rename(columns={
        product_df.columns[0]: 'imageid',
        product_df.columns[1]: 'unitsvariable',
        product_df.columns[2]: 'dollarsvariable'
    })

    # Set up coding map
    coding_map = product_df.set_index('imageid')[['unitsvariable', 'dollarsvariable', group_field.lower()]]
    id_cols = ['record', 'uuid']

    # Process Units
    unit_data = purchase_df[id_cols + coding_map['unitsvariable'].tolist()]
    units_long = unit_data.melt(id_vars=id_cols, var_name='unitsvariable', value_name='Units')
    units_long = units_long.merge(
        coding_map.reset_index()[['unitsvariable', group_field.lower()]], 
        on='unitsvariable', how='left'
    )
    units_long['Units'] = units_long['Units'].fillna(0)
    units_agg = units_long.groupby(['uuid', group_field.lower()], as_index=False)['Units'].sum()

    # Process Dollars
    dollar_data = purchase_df[id_cols + coding_map['dollarsvariable'].tolist()]
    dollars_long = dollar_data.melt(id_vars=id_cols, var_name='dollarsvariable', value_name='Dollars')
    dollars_long = dollars_long.merge(
        coding_map.reset_index()[['dollarsvariable', group_field.lower()]], 
        on='dollarsvariable', how='left'
    )
    dollars_long['Dollars'] = dollars_long['Dollars'].fillna(0)
    dollars_agg = dollars_long.groupby(['uuid', group_field.lower()], as_index=False)['Dollars'].sum()

    # Combine and Pivot
    summary = pd.merge(units_agg, dollars_agg, on=['uuid', group_field.lower()], how='outer').fillna(0)
    pivot = summary.pivot(index='uuid', columns=group_field.lower(), values=['Units', 'Dollars'])
    pivot.columns = [f"{metric}_{label}" for metric, label in pivot.columns]
    return pivot.reset_index()