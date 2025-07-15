{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "eb57b47d",
   "metadata": {},
   "outputs": [],
   "source": [
    "def process_files(product_df, purchase_df):\n",
    "    # Step 1: Build coding map\n",
    "    coding_map = product_df.set_index('ImageID')[['UNITSVARIABLE', 'DOLLARSVARIABLE', 'Category']]\n",
    "    id_cols = ['record', 'uuid']\n",
    "\n",
    "    # Step 2: Process Units\n",
    "    unit_data = purchase_df[id_cols + coding_map['UNITSVARIABLE'].tolist()]\n",
    "    units_long = unit_data.melt(id_vars=id_cols, var_name='UNITSVARIABLE', value_name='Units')\n",
    "    units_long = units_long.merge(\n",
    "        coding_map.reset_index()[['UNITSVARIABLE', 'Category']], \n",
    "        on='UNITSVARIABLE', how='left'\n",
    "    )\n",
    "    units_long['Units'] = units_long['Units'].fillna(0)\n",
    "    units_agg = units_long.groupby(['uuid', 'Category'], as_index=False)['Units'].sum()\n",
    "\n",
    "    # Step 3: Process Dollars\n",
    "    dollar_data = purchase_df[id_cols + coding_map['DOLLARSVARIABLE'].tolist()]\n",
    "    dollars_long = dollar_data.melt(id_vars=id_cols, var_name='DOLLARSVARIABLE', value_name='Dollars')\n",
    "    dollars_long = dollars_long.merge(\n",
    "        coding_map.reset_index()[['DOLLARSVARIABLE', 'Category']], \n",
    "        on='DOLLARSVARIABLE', how='left'\n",
    "    )\n",
    "    dollars_long['Dollars'] = dollars_long['Dollars'].fillna(0)\n",
    "    dollars_agg = dollars_long.groupby(['uuid', 'Category'], as_index=False)['Dollars'].sum()\n",
    "\n",
    "    # Step 4: Merge and Pivot\n",
    "    summary = pd.merge(units_agg, dollars_agg, on=['uuid', 'Category'], how='outer').fillna(0)\n",
    "    pivot = summary.pivot(index='uuid', columns='Category', values=['Units', 'Dollars'])\n",
    "    pivot.columns = [f\"{metric}_{category}\" for metric, category in pivot.columns]\n",
    "    return pivot.reset_index()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
