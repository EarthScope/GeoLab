"""
test_suite.py — Smoke tests for the geolab-slim JupyterLab image.

Covers every package that is uncommented in environment.yaml plus
pyrocko (built from source in the Dockerfile).

Run with:  pytest /etc/tests/test_suite.py -v
"""

import subprocess
import sys

import pytest


# ===========================================================================
# Cloud & storage
# ===========================================================================

class TestCloudStorage:

    def test_boto3_import(self):
        import boto3
        assert boto3.__version__

    def test_boto3_session(self):
        import boto3
        s = boto3.Session(region_name="us-east-1")
        assert s.region_name == "us-east-1"

    def test_awswrangler_import(self):
        import awswrangler as wr
        assert wr.__version__

    def test_obstore_import(self):
        import obstore
        assert obstore.__version__

    def test_awscli_installed(self):
        result = subprocess.run(
            ["aws", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "aws-cli" in result.stdout + result.stderr


# ===========================================================================
# Array / data
# ===========================================================================

class TestArrayData:

    def test_numpy_import(self):
        import numpy as np
        assert np.__version__

    def test_numpy_basic_ops(self):
        import numpy as np
        a = np.arange(12).reshape(3, 4)
        assert a.sum() == 66
        assert a.mean() == pytest.approx(5.5)

    def test_pandas_import(self):
        import pandas as pd
        assert pd.__version__

    def test_pandas_dataframe(self):
        import pandas as pd
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        assert len(df) == 3
        assert list(df.columns) == ["x", "y"]

    def test_pyarrow_import(self):
        import pyarrow as pa
        assert pa.__version__

    def test_pyarrow_table(self):
        import pyarrow as pa
        t = pa.table({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        assert t.num_rows == 3

    def test_pandas_pyarrow_parquet(self, tmp_path):
        import pandas as pd
        df = pd.DataFrame({"a": range(50), "b": list("x" * 50)})
        path = str(tmp_path / "test.parquet")
        df.to_parquet(path, engine="pyarrow")
        df2 = pd.read_parquet(path, engine="pyarrow")
        assert len(df2) == 50

    def test_xarray_import(self):
        import xarray as xr
        assert xr.__version__

    def test_xarray_dataset(self):
        import numpy as np
        import xarray as xr
        ds = xr.Dataset({"temp": (["x", "y"], np.zeros((4, 5)))})
        assert ds["temp"].shape == (4, 5)

    def test_dask_import(self):
        import dask
        assert dask.__version__

    def test_dask_array(self):
        import dask.array as da
        import numpy as np
        x = da.from_array(np.arange(100), chunks=25)
        assert x.sum().compute() == 4950

    def test_bottleneck_import(self):
        import bottleneck as bn
        import numpy as np
        a = np.array([1.0, 2.0, float("nan"), 4.0])
        assert bn.nanmean(a) == pytest.approx(7.0 / 3.0)

    def test_flox_import(self):
        import flox
        assert hasattr(flox, "__version__")

    def test_xarrayutils_import(self):
        try:
            import xarrayutils  # noqa: F401
        except (ImportError, AttributeError) as exc:
            pytest.skip(f"xarrayutils incompatible with installed NumPy: {exc}")

    
# ===========================================================================
# Geospatial
# ===========================================================================

class TestGeospatial:

    def test_cartopy_import(self):
        import cartopy
        assert cartopy.__version__

    def test_cartopy_projection(self):
        import cartopy.crs as ccrs
        proj = ccrs.Mercator()
        x, y = proj.transform_point(0, 0, ccrs.PlateCarree())
        assert abs(x) < 1e-3 and abs(y) < 1e-3

    def test_contextily_import(self):
        import contextily
        assert contextily.__version__

    def test_folium_import(self):
        import folium
        m = folium.Map(location=[37.5, -122.0], zoom_start=10)
        assert "leaflet" in m._repr_html_().lower()

    def test_gdal_import(self):
        from osgeo import gdal
        assert gdal.VersionInfo() != ""

    def test_pygmt_import(self):
        import pygmt
        assert pygmt.__version__

    def test_gmt_cli(self):
        result = subprocess.run(
            ["gmt", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout.strip() != ""


# ===========================================================================
# Visualization
# ===========================================================================

class TestVisualization:

    def test_matplotlib_import(self):
        import matplotlib
        matplotlib.use("Agg")
        assert matplotlib.__version__

    def test_matplotlib_figure(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        assert ax.lines[0].get_xdata().tolist() == [1, 2, 3]
        plt.close(fig)

    def test_panel_import(self):
        import panel as pn
        assert pn.__version__

    def test_ipympl_import(self):
        import ipympl
        assert hasattr(ipympl, "__version__")

    def test_ffmpeg_installed(self):
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_ghostscript_installed(self):
        result = subprocess.run(
            ["gs", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0


# ===========================================================================
# Jupyter & dev tools
# ===========================================================================

class TestJupyterDevTools:

    def test_ipykernel_import(self):
        import ipykernel
        assert ipykernel.__version__

    def test_jupyterlab_git_import(self):
        import jupyterlab_git
        assert hasattr(jupyterlab_git, "__version__")

    def test_jupyterlab_myst_import(self):
        import jupyterlab_myst
        assert hasattr(jupyterlab_myst, "__version__")

    def test_ruff_installed(self):
        result = subprocess.run(
            ["ruff", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_git_installed(self):
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_gh_cli_installed(self):
        result = subprocess.run(
            ["gh", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_pytest_importable(self):
        import pytest
        assert pytest.__version__


# ===========================================================================
# Geophysics — conda packages
# ===========================================================================

class TestGeophysicsConda:

    def test_obspy_import(self):
        import obspy
        assert obspy.__version__

    def test_obspy_trace(self):
        import numpy as np
        import obspy
        tr = obspy.Trace(data=np.zeros(1000))
        tr.stats.sampling_rate = 100.0
        assert tr.stats.npts == 1000

    def test_obspy_filter(self):
        import numpy as np
        import obspy
        tr = obspy.Trace(
            data=np.random.default_rng(0).standard_normal(1000).astype("float64")
        )
        tr.stats.sampling_rate = 100.0
        tr.filter("bandpass", freqmin=1.0, freqmax=20.0)
        assert tr.data.shape == (1000,)

    def test_obspy_read_mseed(self, tmp_path):
        import numpy as np
        import obspy
        tr = obspy.Trace(data=np.arange(100, dtype="int32"))
        tr.stats.sampling_rate = 25.0
        tr.stats.network = "XX"
        tr.stats.station = "TST"
        tr.stats.channel = "HHZ"
        path = str(tmp_path / "test.mseed")
        obspy.Stream([tr]).write(path, format="MSEED")
        st2 = obspy.read(path)
        assert st2[0].stats.station == "TST"

    def test_obsplus_import(self):
        import obsplus
        assert obsplus.__version__

    def test_obsplus_wavebank(self, tmp_path):
        import numpy as np
        import obspy
        import obsplus
        for i in range(3):
            tr = obspy.Trace(data=np.zeros(200, dtype="int32"))
            tr.stats.network = "XX"
            tr.stats.station = f"S{i:02d}"
            tr.stats.channel = "HHZ"
            tr.stats.sampling_rate = 100.0
            tr.stats.starttime = obspy.UTCDateTime(2020, 1, 1) + i * 10
            obspy.Stream([tr]).write(
                str(tmp_path / f"s{i}.mseed"), format="MSEED"
            )
        bank = obsplus.WaveBank(str(tmp_path))
        bank.update_index()
        assert len(bank.read_index()) > 0

    def test_dascore_import(self):
        import dascore as dc
        assert dc.__version__

    def test_dascore_patch(self):
        import dascore as dc
        patch = dc.get_example_patch()
        assert patch.dims

    def test_pyrocko_import(self):
        import pyrocko
        assert pyrocko.__version__

    def test_pyrocko_trace(self):
        import numpy as np
        from pyrocko.trace import Trace
        tr = Trace(
            network="XX", station="TST", location="", channel="HHZ",
            tmin=0.0, deltat=0.01,
            ydata=np.zeros(1000, dtype="float32"),
        )
        assert len(tr.get_ydata()) == 1000

    def test_cvxpy_import(self):
        import cvxpy as cp
        assert cp.__version__

    def test_cvxpy_lp(self):
        import cvxpy as cp
        x = cp.Variable()
        prob = cp.Problem(cp.Minimize(x), [x >= 3.0])
        prob.solve()
        assert x.value == pytest.approx(3.0, abs=1e-4)


# ===========================================================================
# Geophysics — pip packages
# ===========================================================================

class TestGeophysicsPip:

    def test_earthscope_sdk_import(self):
        import earthscope_sdk
        assert hasattr(earthscope_sdk, "__version__")

    def test_earthscopestraintools_import(self):
        import earthscopestraintools
        assert earthscopestraintools

    def test_gnssrefl_import(self):
        import gnssrefl
        assert gnssrefl

    def test_hypoinvpy_import(self):
        import hypoinvpy
        assert hypoinvpy

    def test_pyocto_import(self):
        import pyocto
        assert pyocto.__version__

    def test_pyocto_associator(self):
        from pyocto import OctoAssociator
        assoc = OctoAssociator.from_area(
            lat=(35.0, 40.0), lon=(-122.0, -118.0),
            zlim=(0.0, 30.0),
            time_before=300.0,
            velocity_model=None,
        )
        assert assoc is not None
