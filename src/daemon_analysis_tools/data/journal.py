from typing import Dict, Union

import pandas as pd


class Journal:
    def __init__(self, name: str, data: pd.DataFrame) -> None:
        """
        Initialize a Journal instance.

        :param name: The name of the journal.
        :param data: A dictionary or pandas Series containing the data for the journal.
        """
        self.name = name
        self.has_rdp = self._parse_rdp(data)
        self.data_sharing_requirements = self._parse_data_sharing_requirements(data)
        self.fair_data_sharing = self._parse_fair_data_sharing(data)
        self.data_availability_statement = self._parse_data_availability_statement(data)

    def __repr__(self) -> None:
        return f"""Journal(name={self.name},
        has_rdp={self.has_rdp},
        data_sharing_requirements={self.data_sharing_requirements},
        fair_data_sharing={self.fair_data_sharing},
        data_availability_statement={self.data_availability_statement})"""

    def _parse_rdp(self, data: Union[pd.DataFrame, Dict]) -> bool:
        return (
            data.get("1. Existence of research data policy")
            == "Research Data Policy (RDP) exists."
            or data.get(1) == "Research Data Policy (RDP) exists."
        )

    def _parse_data_sharing_requirements(self, data: Union[pd.DataFrame, Dict]) -> str:
        dsr = data.get("3. Data sharing requirements in RDP") or data.get(3, "Unknown")
        if dsr == "Data sharing only with editors and referees (no public sharing)":
            return "no_public_sharing"
        elif dsr == "Data sharing encouraged but optional.":
            return "encouraged"
        elif dsr == (
            "Data sharing required but not publicly (e.g. available "
            "upon request is allowed)."
        ):
            return "available_upon_request"
        elif dsr == "Public data sharing required only for specific types of data.":
            return "only_specific"
        elif dsr == "Public data sharing of all data required.":
            return "all_data"
        else:
            raise ValueError("Data sharing requirements information not present")

    def _parse_fair_data_sharing(self, data: pd.DataFrame) -> str:
        fds = data.get(
            (
                "4. FAIR data sharing (see https://www.go-fair.org/fair-principles/ "
                "for a definition of FAIR)"
            )
        ) or data.get(4, "Unknown")

        if fds == "Public data sharing on a FAIR repository not mentioned in RDP.":
            return "no_FAIR"
        elif fds == "Public data sharing on a FAIR repository encouraged.":
            return "encouraged"
        elif fds == (
            "Public data sharing on a FAIR repository required only for specific "
            "types of data (e.g. genetic data has to be shared on a FAIR repository "
            "but no other data)."
        ):
            return "only_specific"
        elif fds == "Public data sharing of all data on a FAIR repository required.":
            return "all_data"
        else:
            raise ValueError("FAIR data sharing information not present")

    def _parse_data_availability_statement(
        self, data: Union[pd.DataFrame, Dict]
    ) -> str:
        das = data.get("2. Data availability statement") or data.get(2, "Unknown")
        if das == "Not mentioned in the RDP.":
            return "not_mentioned"
        elif das == "Mentioned in the RDP but optional.":
            return "optional"
        elif das == "Required according to the RDP.":
            return "required"
        else:
            raise ValueError("Data availability statement information not present")

    # Add more parsing methods for other attributes
