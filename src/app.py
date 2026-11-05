# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App

from src.actions import register_actions
from src.asset import Asset
from src.test_connectivity import run_test_connectivity


def create_crits_app() -> App:
    app = App(
        name="CRITs",
        app_type="siem",
        logo="logo_crits.svg",
        logo_dark="logo_crits_dark.svg",
        product_vendor="MITRE",
        product_name="CRITs",
        publisher="Splunk",
        appid="ef9cfabb-f011-43c3-bc8b-0ef30a04bf35",
        fips_compliant=True,
        encrypt_cache_state=True,
        encrypt_ingest_state=True,
        asset_cls=Asset,
    )

    @app.test_connectivity()
    def test_connectivity(soar: SOARClient, asset: Asset) -> None:
        run_test_connectivity(soar, asset)

    return register_actions(app)


app = create_crits_app()


if __name__ == "__main__":
    app.cli()
