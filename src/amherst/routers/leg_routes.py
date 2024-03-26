
# @router.get(
#     '/pcneighbours/{booking_id}/{postcode}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def pcneighbours(
#         booking_id: int,
#         postcode: str,
#         pfcom: AmShipper = Depends(get_pfc),
#         session: Session = Depends(get_session),
# ):
#     man_in = await get_manager(booking_id, session)
#     man_out = managers.BookingManagerOut.model_validate(man_in)
#     candidates = pfcom.get_candidates(postcode)
#     return await shipping_page.address_chooser2(
#         manager=man_out,
#         candidates=candidates
#     )
