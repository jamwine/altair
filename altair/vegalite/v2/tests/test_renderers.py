"""Tests of various renderers"""

import pytest

import altair as alt


@pytest.fixture
def chart():
    return alt.Chart('data.csv').mark_point()


def test_colab_renderer_embed_options(chart):
    """Test that embed_options in renderer metadata are correctly manifest in html"""
    def assert_actions_true(chart):
        bundle = chart._repr_mimebundle_(None, None)
        html = bundle['text/html']
        assert ('embedOpt = {"actions": true, "mode": "vega-lite"}' in html or
                'embedOpt = {"mode": "vega-lite", "actions": true}' in html)

    def assert_actions_false(chart):
        bundle = chart._repr_mimebundle_(None, None)
        html = bundle['text/html']
        assert ('embedOpt = {"actions": false, "mode": "vega-lite"}' in html or
                'embedOpt = {"mode": "vega-lite", "actions": false}' in html)

    with alt.renderers.enable('colab', embed_options=dict(actions=False)):
        assert_actions_false(chart)

    with alt.renderers.enable('colab'):
        with alt.renderers.enable(embed_options=dict(actions=True)):
            assert_actions_true(chart)

        with alt.renderers.set_embed_options(actions=False):
            assert_actions_false(chart)

        with alt.renderers.set_embed_options(actions=True):
            assert_actions_true(chart)


def test_default_renderer_embed_options(chart, renderer='default'):
    # check that metadata is passed appropriately
    mimetype = alt.display.VEGALITE_MIME_TYPE
    spec = chart.to_dict()
    with alt.renderers.enable(renderer, embed_options=dict(actions=False)):
        bundle, metadata = chart._repr_mimebundle_(None, None)
        assert set(bundle.keys()) == {mimetype, 'text/plain'}
        assert bundle[mimetype] == spec
        assert metadata == {mimetype: {'embed_options': {'actions': False}}}

    # Sanity check: no metadata specified
    with alt.renderers.enable(renderer):
        bundle, metadata = chart._repr_mimebundle_(None, None)
        assert bundle[mimetype] == spec
        assert metadata == {}


def test_json_renderer_embed_options(chart, renderer='json'):
    """Test that embed_options in renderer metadata are correctly manifest in html"""
    mimetype = 'application/json'
    spec = chart.to_dict()
    with alt.renderers.enable('json', option='foo'):
        bundle, metadata = chart._repr_mimebundle_(None, None)
        assert set(bundle.keys()) == {mimetype, 'text/plain'}
        assert bundle[mimetype] == spec
        assert metadata == {mimetype: {'option': 'foo'}}

    # Sanity check: no options specified
    with alt.renderers.enable(renderer):
        bundle, metadata = chart._repr_mimebundle_(None, None)
        assert bundle[mimetype] == spec
        assert metadata == {}
