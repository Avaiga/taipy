from taipy.gui.utils import _MapDictionary


def test_mapdict():

    d = {"a": 1, "b": 2, "c": 3}
    md = _MapDictionary(d)
    md_copy = _MapDictionary(d).copy()
    assert len(md) == 3
    assert md.__getitem__("a") == d["a"]
    md.__setitem__("a", 4)
    assert md.__getitem__("a") == 4
    assert d["a"] == 4
    v1 = d["b"]
    v2 = md.pop("b")
    assert v1 == v2
    assert "b" not in d.keys()
    assert "c" in md
    assert len(md) == 2
    v1 = d["c"]
    v2 = md.popitem()
    assert v2 == ("c", v1)
    assert len(md) == 1
    md.clear()
    assert len(md) == 0
    assert len(d) == 0
    assert len(md_copy) == 3
    v1 = ""
    for k in md_copy:
        v1 += k
    assert v1 == "abc"
    v1 = ""
    for k in md_copy.keys():
        v1 += k
    assert v1 == "abc"
    v1 = ""
    for k in md_copy.__reversed__():
        v1 += k
    assert v1 == "cba"
    v1 = 0
    for k in md_copy.values():
        v1 += k
    assert v1 == 6  # 1+2+3
    v1 = md_copy.setdefault("a", 5)
    assert v1 == 1
    v1 = md_copy.setdefault("d", 5)
    assert v1 == 5

    try:
        md = _MapDictionary("not_a_dict")
        assert False
    except Exception:
        assert True
    pass


def test_mapdict_update():
    update_values = {}

    def update(k, v):
        update_values[0] = k
        update_values[1] = v
        pass

    d = {"a": 1, "b": "2"}
    md = _MapDictionary(d, update)
    md.__setitem__("a", 3)
    assert update_values[0] == "a"
    assert update_values[1] == 3
    print("")
    pass
