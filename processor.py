import pandas as pd

def process_files(product_df, purchase_df, group_field='Category'):
    coding_map = product_df.set_index('ImageID')[['UNITSVARIABLE', 'DOLLARSVARIABLE', group_field]]
    id_cols = ['record', 'uuid']

    # Process Units
    unit_data = purchase_df[id_cols + coding_map['UNITSVARIABLE'].tolist()]
    units_long = unit_data.melt(id_vars=id_cols, var_name='UNITSVARIABLE', value_name='Units')
    units_long = units_long.merge(
        coding_map.reset_index()[['UNITSVARIABLE', group_field]], 
        on='UNITSVARIABLE', how='left'
    )
    units_long['Units'] = units_long['Units'].fillna(0)
    units_agg = units_long.groupby(['uuid', group_field], as_index=False)['Units'].sum()

    # Process Dollars
    dollar_data = purchase_df[id_cols + coding_map['DOLLARSVARIABLE'].tolist()]
    dollars_long = dollar_data.melt(id_vars=id_cols, var_name='DOLLARSVARIABLE', value_name='Dollars')
    dollars_long = dollars_long.merge(
        coding_map.reset_index()[['DOLLARSVARIABLE', group_field]], 
        on='DOLLARSVARIABLE', how='left'
    )
    dollars_long['Dollars'] = dollars_long['Dollars'].fillna(0)
    dollars_agg = dollars_long.groupby(['uuid', group_field], as_index=False)['Dollars'].sum()

    # Combine and Pivot
    summary = pd.merge(units_agg, dollars_agg, on=['uuid', group_field], how='outer').fillna(0)
    pivot = summary.pivot(index='uuid', columns=group_field, values=['Units', 'Dollars'])
    pivot.columns = [f"{metric}_{label}" for metric, label in pivot.columns]
    return pivot.reset_index()

