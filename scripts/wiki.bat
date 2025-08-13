start R:\paul_r\docs\index.html
if %errorlevel% neq 0 (
    echo An error occurred.
    pause
) else (
    echo Success.
)
popd