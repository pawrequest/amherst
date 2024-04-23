from __future__ import annotations

import typing as _t

ModelKind: _t.TypeAlias = _t.Literal['zero', 'minimum', 'simple', 'collect']  # noqa: UP040
valid_model_kinds = _t.get_args(ModelKind)


