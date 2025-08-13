cd C:\prdev\repos\amdev\amherst
uv run shipper %1 %2 %3
if %errorlevel% neq 0 (
    echo An error occurred.
    pause
) else (
    echo Success.
)
popd