import pandas as pd
from processor import process_files

def test_nan_vs_zero_handling():
    # Sample product coding
    product_df = pd.DataFrame({
        'ImageID': ['P1'],
        'Units Variable': ['prod1'],
        'Dollars Variable': ['prod1$'],
        'Category': ['Snacks']
    })

    # Purchase data with NaN values
    purchase_df = pd.DataFrame({
        'record': [101, 102],
        'uuid': ['a1', 'a2'],
        'prod1': [None, 0],
        'prod1$': [None, 0]
    })

    result = process_files(product_df, purchase_df, group_field='Category')

    # First row should be NaN
    assert pd.isna(result.loc[0, 'Units_Snacks']), "Expected NaN for Units when input is all NaN"
    assert pd.isna(result.loc[0, 'Dollars_Snacks']), "Expected NaN for Dollars when input is all NaN"

    # Second row should be 0
    assert result.loc[1, 'Units_Snacks'] == 0, "Expected 0 for Units when input includes 0"
    assert result.loc[1, 'Dollars_Snacks'] == 0, "Expected 0 for Dollars when input includes 0"
