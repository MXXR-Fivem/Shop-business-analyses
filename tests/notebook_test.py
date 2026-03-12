from testbook import testbook


@testbook(
    'notebook.ipynb',
    execute=['imports', 'load_datasets', 'merge_datasets', 'get_best_sellers'],
)
def test_get_best_sellers_type(tb):
    func = tb.get('get_best_sellers')

    result = func()
    assert hasattr(result, 'isna')


@testbook(
    'notebook.ipynb',
    execute=['imports', 'load_datasets', 'merge_datasets', 'aisles_dep_selling_rate'],
)
def test_aisles_dep_selling_rate(tb):
    func = tb.get('aisles_dep_selling_rate')

    result_dep = func('department', 5)
    print(result_dep.shape)
    assert hasattr(result_dep, 'isna') and result_dep.shape[0] == 5

    func('aisle', 5)
    print(result_dep.shape)
    assert hasattr(result_dep, 'isna') and result_dep.shape[0] == 5


if __name__ == '__main__':
    test_get_best_sellers_type()
    test_aisles_dep_selling_rate()
    print('OK, ALL TEST PASSED')
