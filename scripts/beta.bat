cd C:\prdev\amdev\amherst
uv run shipper %1 %2 %3
if %errorlevel% neq 0 (
    pause
) else (
)
popd