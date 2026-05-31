"""
Unit tests for packages installed in geolab-base.

Run inside the container:
    pytest test_packages.py -v

Run with a filter:
    pytest test_packages.py -v -k geospatial    # tests with 'geospatial' in name
    pytest test_packages.py::test_obspy -v      # single test

Each test exercises one package with a minimal API call. Failures usually
indicate ABI mismatches, missing system libraries, or broken installs --
NOT just missing imports, which a smoke check would also catch.
"""

import math
import shutil
import subprocess

import pytest

# ─── Helpers ──────────────────────────────────────────────────


def _cli_version(cmd, version_flag="--version"):
    """Run `cmd --version` and return stdout. Fail if not on $PATH."""
    if not shutil.which(cmd):
        pytest.fail(f"{cmd} not on $PATH")
    r = subprocess.run(
        [cmd, version_flag],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return (r.stdout or r.stderr).strip()


# ─── Cloud & storage ──────────────────────────────────────────


def test_aws_cli():
    out = _cli_version("aws")
    assert "aws-cli" in out.lower()


def test_awswrangler():
    import awswrangler as wr

    assert wr.__version__


def test_boto3():
    import boto3

    client = boto3.client("s3", region_name="us-east-1")
    assert client.meta.service_model.service_name == "s3"


def test_obstore():
    import obstore  # noqa: F401


# ─── Geospatial ───────────────────────────────────────────────


def test_cartopy():
    import cartopy.crs as ccrs

    proj = ccrs.PlateCarree()
    assert proj.proj4_params is not None


def test_contextily():
    import contextily as cx

    assert cx.__version__


def test_fiona():
    import fiona

    drivers = fiona.supported_drivers
    assert "GPKG" in drivers
    assert "ESRI Shapefile" in drivers


def test_folium():
    import folium

    m = folium.Map(location=[0, 0], zoom_start=2)
    assert m is not None


def test_gdal():
    from osgeo import gdal

    release = gdal.VersionInfo("RELEASE_NAME")
    assert release  # e.g. "3.8.4"


def test_pyproj():
    import pyproj

    crs = pyproj.CRS("EPSG:4326")
    assert crs.to_epsg() == 4326
    assert "WGS 84" in crs.name


def test_shapely():
    from shapely.geometry import Point

    p = Point(0, 0)
    assert p.buffer(1).area == pytest.approx(math.pi, abs=0.1)


# ─── Core scientific stack ────────────────────────────────────


def test_numpy():
    import numpy as np

    assert int(np.array([1, 2, 3]).sum()) == 6


def test_scipy():
    from scipy import stats

    assert stats.norm.cdf(0) == pytest.approx(0.5)


def test_pandas():
    import pandas as pd

    df = pd.DataFrame({"a": [1, 2, 3]})
    assert df.shape == (3, 1)
    assert df["a"].sum() == 6


def test_geopandas():
    import geopandas as gpd
    from shapely.geometry import Point

    gdf = gpd.GeoDataFrame(
        {"name": ["a", "b"]},
        geometry=[Point(0, 0), Point(1, 1)],
        crs="EPSG:4326",
    )
    assert len(gdf) == 2
    assert gdf.crs.to_epsg() == 4326


def test_matplotlib():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    plt.close(fig)


def test_xarray():
    import xarray as xr

    da = xr.DataArray([1, 2, 3], dims="x")
    assert da.sum().item() == 6


def test_netcdf4(tmp_path):
    import netCDF4

    path = tmp_path / "smoke.nc"
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("x", 3)
        v = ds.createVariable("v", "f4", ("x",))
        v[:] = [1.0, 2.0, 3.0]
    with netCDF4.Dataset(path, "r") as ds:
        assert ds["v"][:].sum() == pytest.approx(6.0)


def test_h5py(tmp_path):
    import h5py
    import numpy as np

    path = tmp_path / "smoke.h5"
    with h5py.File(path, "w") as f:
        f["arr"] = np.arange(3)
    with h5py.File(path, "r") as f:
        assert f["arr"][:].sum() == 3


def test_pyarrow():
    import pyarrow as pa

    arr = pa.array([1, 2, 3])
    assert arr.to_pylist() == [1, 2, 3]


def test_bottleneck():
    import bottleneck as bn

    assert bn.nansum([1.0, 2.0, float("nan"), 3.0]) == pytest.approx(6.0)


def test_flox():
    import flox

    assert flox.__version__


def test_xarrayutils():
    import xarrayutils  # noqa: F401


# ─── Parallel computing ───────────────────────────────────────


def test_dask():
    import dask.array as da

    assert da.ones(10, chunks=5).sum().compute() == pytest.approx(10.0)


def test_dask_gateway():
    import dask_gateway  # noqa: F401


def test_distributed():
    import distributed

    assert distributed.__version__


# ─── Geo / geoscience ─────────────────────────────────────────


def test_dascore():
    import dascore

    assert hasattr(dascore, "__version__")


def test_gmt_cli():
    out = _cli_version("gmt")
    assert "gmt" in out.lower()


def test_obspy():
    from obspy import UTCDateTime

    t = UTCDateTime("2020-01-01T12:30:45")
    assert t.year == 2020
    assert t.month == 1
    assert t.hour == 12


def test_pygmt():
    import pygmt

    assert pygmt.__version__


def test_obsplus():
    import obsplus  # noqa: F401


# ─── Optimization ─────────────────────────────────────────────


def test_cvxpy():
    import cvxpy as cp

    x = cp.Variable()
    prob = cp.Problem(cp.Minimize((x - 2) ** 2))
    prob.solve()
    assert x.value == pytest.approx(2.0, abs=1e-3)


# ─── Visualization ────────────────────────────────────────────


def test_ipympl():
    import ipympl  # noqa: F401


def test_panel():
    import panel as pn

    assert pn.__version__


def test_vl_convert():
    import vl_convert as vlc

    assert vlc.__version__


# ─── Media & system tools ─────────────────────────────────────


def test_ghostscript_cli():
    out = _cli_version("gs", "--version")
    assert any(ch.isdigit() for ch in out)


def test_ffmpeg_cli():
    out = _cli_version("ffmpeg", "-version")
    assert "ffmpeg" in out.lower()


# ─── Utilities ────────────────────────────────────────────────


def test_tqdm():
    from tqdm import tqdm

    assert list(tqdm(range(3), disable=True)) == [0, 1, 2]


def test_requests():
    import requests

    assert requests.__version__


def test_pyyaml():
    import yaml

    parsed = yaml.safe_load("a: 1\nb: [2, 3]")
    assert parsed == {"a": 1, "b": [2, 3]}


# ─── Dev tools ────────────────────────────────────────────────


def test_gh_cli():
    out = _cli_version("gh")
    assert "gh version" in out.lower() or "github cli" in out.lower()


def test_gh_scoped_creds():
    assert shutil.which("gh-scoped-creds") is not None


def test_pytest_self():
    # we're in pytest, so importing it must work
    assert pytest.__version__


def test_ruff_cli():
    out = _cli_version("ruff")
    assert "ruff" in out.lower()


# ─── Jupyter stack & extensions ───────────────────────────────


def test_jupyterhub():
    import jupyterhub

    assert jupyterhub.__version__


def test_jupyter_server():
    import jupyter_server

    assert jupyter_server.__version__


def test_jupyterlab():
    import jupyterlab

    assert jupyterlab.__version__


def test_ipykernel():
    import ipykernel

    assert ipykernel.__version__


def test_jupyter_resource_usage():
    import jupyter_resource_usage  # noqa: F401


def test_jupyter_ruff():
    import jupyter_ruff  # noqa: F401


def test_jupyter_server_proxy():
    import jupyter_server_proxy  # noqa: F401


def test_jupyterlab_git():
    import jupyterlab_git  # noqa: F401


def test_jupyterlab_myst():
    import jupyterlab_myst  # noqa: F401


def test_jupyterlab_code_formatter():
    import jupyterlab_code_formatter  # noqa: F401


def test_jupyterlab_pygments():
    import jupyterlab_pygments  # noqa: F401


def test_nbdime():
    import nbdime

    assert nbdime.__version__


# ─── pip packages ─────────────────────────────────────────────


def test_earthscope_sdk():
    import earthscope_sdk  # noqa: F401


def test_earthscope_cli():
    # `es` is the earthscope-cli entry point
    assert shutil.which("es") is not None


def test_earthscopestraintools():
    import earthscopestraintools  # noqa: F401


def test_jupyterlab_jupyterbook_navigation():
    import jupyterlab_jupyterbook_navigation  # noqa: F401


def test_altair():
    import altair as alt

    chart = alt.Chart()
    assert chart is not None


def test_plotly():
    import plotly

    assert plotly.__version__


def test_polars():
    import polars as pl

    df = pl.DataFrame({"a": [1, 2, 3]})
    assert df.shape == (3, 1)
    assert df["a"].sum() == 6


def test_vegafusion():
    import vegafusion  # noqa: F401
