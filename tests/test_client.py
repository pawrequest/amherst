from __future__ import annotations

import os
from pathlib import Path

from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from pydantic import BaseModel, ConfigDict
from thefuzz import fuzz, process
from zeep import Client
from zeep.proxy import ServiceProxy

from shipr.models import el_msg as msg, service_protocols as cp, extended, shipr_shared as shared

SCORER = fuzz.token_sort_ratio


class ZeepConfig(BaseModel):
    auth: shared.Authentication
    binding: str
    wsdl: str
    endpoint: str

    @classmethod
    def from_env(cls):
        return cls(
            auth=shared.Authentication.from_env(),
            binding=os.environ.get("PF_BINDING"),
            wsdl=os.environ.get("PF_WSDL"),
            endpoint=os.environ.get("PF_ENDPOINT_SAND"),
        )


def get_service(client, binding, endpoint) -> ServiceProxy:
    return client.create_service(binding_name=binding, address=endpoint)


class ELClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: ZeepConfig
    service: ServiceProxy

    @classmethod
    def from_config(cls, config: ZeepConfig):
        client = Client(wsdl=config.wsdl)
        service = client.create_service(config.binding, config.endpoint)
        return cls(config=config, service=service)

    @classmethod
    # @lru_cache(maxsize=1)
    def from_env(cls):
        return cls.from_config(ZeepConfig.from_env())

    def new_service(self) -> ServiceProxy:
        client = Client(wsdl=self.config.wsdl)
        serv = client.create_service(binding_name=self.config.binding, address=self.config.endpoint)
        return serv

    def backend(self, service_prot: type[ServiceProtocolT]) -> ServiceProxy:
        return ZeepBackend(self.service)[service_prot]

    def get_shipment_resp(self, req: msg.CreateShipmentRequest) -> msg.CreateShipmentResponse:
        back = self.backend(cp.CreateShipmentService)
        resp = back.createshipment(request=req.model_dump(by_alias=True))
        return msg.CreateShipmentResponse.model_validate(resp)

    def get_candidates(self, postcode: str) -> list[extended.AddressRecipient]:
        req = msg.FindRequest(authentication=self.config.auth, paf=extended.PAF(postcode=postcode))
        back = self.backend(cp.FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if paf := response.paf:
            ret = [neighbour.address[0] for neighbour in paf.specified_neighbour]
        else:
            ret = []
        return ret

    def get_label(self, ship_num) -> Path:
        """Get the label for a shipment number.

        args:
            pf_com2: PFCom - PFCom combadge client
            pf_auth: elt.Authentication - PFCom authentication
            ship_num: str - shipment number
        """
        back = self.backend(cp.PrintLabelService)
        req = msg.PrintLabelRequest(authentication=self.config.auth, shipment_number=ship_num)
        response: msg.PrintLabelResponse = back.printlabel(request=req)
        out_path = response.label.download()
        os.startfile(out_path)
        return out_path

    def choose_address(self, address: extended.AddressRecipient) -> extended.AddressRecipient | None:
        candidates = self.candidates_dict(address.postcode)
        if not candidates:
            return None
        chosen, score = process.extractOne(address.address_lines_str(), list(candidates.keys()), scorer=SCORER)
        add = candidates[chosen]
        return add

    def candidates_dict(self, postcode):
        candidates_dict = {add.address_lines_str(): add for add in self.get_candidates(postcode)}
        return candidates_dict

    def address_choice_str(self, address_lines: str, postcode: str) -> extended.AddressChoice:
        candidates_dict = self.candidates_dict(postcode)
        chosen, score = process.extractOne(address_lines, list(candidates_dict.keys()), scorer=SCORER)
        add = candidates_dict[chosen]
        return extended.AddressChoice(address=add, score=score)
