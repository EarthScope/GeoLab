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
import re
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


def test_fsspec():
    import fsspec

    fs = fsspec.filesystem("memory")
    assert fs.protocol == "memory"


def test_s3fs():
    import s3fs

    assert s3fs.S3FileSystem is not None


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


def test_ipyleaflet():
    import ipyleaflet

    m = ipyleaflet.Map()
    assert m is not None


def test_lonboard():
    import lonboard

    assert lonboard.__version__


# ─── Core scientific stack ────────────────────────────────────


def test_numpy():
    import numpy as np

    assert int(np.array([1, 2, 3]).sum()) == 6


def test_numba():
    from numba import njit

    @njit
    def add_one(x):
        return x + 1

    assert add_one(1) == 2


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


def test_matplotlib_base():
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


@pytest.mark.filterwarnings("ignore:numpy.ndarray size changed:RuntimeWarning")
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


def test_h5netcdf(tmp_path):
    import h5netcdf.legacyapi as netCDF4
    import numpy as np

    path = tmp_path / "smoke_h5netcdf.nc"
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("x", 3)
        v = ds.createVariable("v", "f4", ("x",))
        v[:] = np.array([1.0, 2.0, 3.0])
    with netCDF4.Dataset(path, "r") as ds:
        assert ds["v"][:].sum() == pytest.approx(6.0)


def test_zarr():
    import zarr

    arr = zarr.zeros((3,), chunks=3, dtype="f4")
    arr[:] = [1.0, 2.0, 3.0]
    assert arr[:].sum() == pytest.approx(6.0)


def test_virtualizarr():
    import virtualizarr  # noqa: F401

    assert virtualizarr.__version__


def test_pooch():
    import pooch

    assert pooch.__version__


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
    import dascore as dc
    
    patch = dc.get_example_patch("random_das")   # synthetic DAS data, no download
    
    assert "time" in patch.dims
    assert "distance" in patch.dims
    sizes = dict(zip(patch.dims, patch.data.shape))
    assert sizes["time"] > 0 and sizes["distance"] > 0
    
    decimated = patch.decimate(time=8) 
    dec_sizes = dict(zip(decimated.dims, decimated.data.shape))
    assert dec_sizes["time"] < sizes["time"]            # fewer time samples
    assert dec_sizes["distance"] == sizes["distance"]   # distance unchanged


def test_gmt_cli():
    #engine and map data are tested through test_pygmt
    out = _cli_version("gmt") 
    assert re.match(r"\d+\.\d+", out.strip())  # gmt --version prints bare "6.6.0"


def test_obspy():
    import obspy
    
    st = obspy.read()   # bundled 3-trace example seismogram that comes with obspy
    
    assert len(st) == 3 #checks the stream contains exactly three traces
    tr = st[0] 
    assert tr.stats.sampling_rate > 0 
    assert tr.stats.npts == len(tr.data)   
    # Run a real signal-processing step: a bandpass filter (1–10 Hz).
    n_before = tr.stats.npts
    st.filter("bandpass", freqmin=1.0, freqmax=10.0)
    assert st[0].stats.npts == n_before          # filtering preserves sample count
    assert st[0].data.shape == (n_before,)       # still a populated 1-D waveform


def test_pygmt(tmp_path):
    import pygmt
    
    fig = pygmt.Figure()
    fig.coast(
      region=[-10, 10, -10, 10],
      projection="M6c",
      land="gray",
      water="lightblue",
      shorelines="1/0.5p",   
      borders="1/0.5p",      
    )
    out = tmp_path / "coast.png"
    fig.savefig(out)
    assert out.exists()
    assert out.stat().st_size > 0


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


def test_hvplot():
    import hvplot  # noqa: F401

    assert hvplot.__version__


def test_holoviews():
    import holoviews as hv

    curve = hv.Curve([1, 2, 3])
    assert curve is not None


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


# ─── Interactive widgets ───────────────────────────────────────


def test_ipywidgets():
    import ipywidgets

    slider = ipywidgets.IntSlider(value=5, min=0, max=10)
    assert slider.value == 5


def test_anywidget():
    import anywidget  # noqa: F401

    assert anywidget.__version__


@pytest.mark.filterwarnings("ignore:metadata .* was set from the constructor:DeprecationWarning")
def test_bqplot():
    import bqplot  # noqa: F401

    assert bqplot.__version__


def test_ipytree():
    from ipytree import Node

    root = Node(name="root")
    assert root.name == "root"


def test_itables():
    import itables  # noqa: F401

    assert itables.__version__


def test_ipydatagrid():
    import ipydatagrid  # noqa: F401

    assert ipydatagrid.__version__


def test_sidecar():
    from sidecar import Sidecar  # noqa: F401
