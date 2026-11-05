from soar_sdk.asset import AssetField, BaseAsset, FieldCategory


class Asset(BaseAsset):
    url: str = AssetField(
        description="Device URL e.g. https://mycrits.contoso.com:8080",
        category=FieldCategory.CONNECTIVITY,
    )
    verify_server_cert: bool = AssetField(
        description="Verify server certificate", default=True, category=FieldCategory.CONNECTIVITY
    )
    username: str = AssetField(description="Username", category=FieldCategory.CONNECTIVITY)
    api_key: str = AssetField(description="API Key", sensitive=True, category=FieldCategory.CONNECTIVITY)
    timeout: float = AssetField(
        description="Request Timeout (Default: 30 seconds)",
        default=30.0,
        category=FieldCategory.CONNECTIVITY,
    )
