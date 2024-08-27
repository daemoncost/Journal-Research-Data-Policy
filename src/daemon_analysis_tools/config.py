# Some info

question_num_to_text = {
    1: "1. Existence of research data policy",
    3: "3. Data sharing requirements in RDP",
    4: "4. FAIR data sharing (see https://www.go-fair.org/fair-principles/ for a definition of FAIR)",
    2: "2. Data availability statement",
    5: "5. Citability and findability of data ",
    7: "7. Timing of data release",
    8: "8. Recommended data sharing method",
    9: "9. Recommended/required licenses",
    10: "10. Referee guidelines concerning research data",
    13: "13. Code sharing requirements",
    14: "14. Code Reproducibility",
    15: "15. Versioning and persistent identifiers",
    16: "16. Code Quality Standards",
    17: "17. Automatic Testing",
    18: "18. Code Documentation",
    19: "19. Linting Standards",
    20: "20. Code Development",
}

multiple_choice_columns = [
    "1. Existence of research data policy",
    "3. Data sharing requirements in RDP",
    "4. FAIR data sharing (see https://www.go-fair.org/fair-principles/ for a definition of FAIR)",
    "2. Data availability statement",
    "5. Citability and findability of data ",
    "7. Timing of data release",
    "8. Recommended data sharing method",
    "9. Recommended/required licenses",
    "10. Referee guidelines concerning research data",
    "13. Code sharing requirements",
    "14. Code Reproducibility",
    "15. Versioning and persistent identifiers",
    "16. Code Quality Standards",
    "17. Automatic Testing",
    "18. Code Documentation",
    "19. Linting Standards",
    "20. Code Development",
]

open_text_columns = [
    "11. Unique policies for data types\nPlease name all data types for which unique policies are recommended according to the RDP (Please separate all data types be semicolon, e.g. crystal structures; Protein sequence)",
    "12. Unique policies for data types\nPlease name all data types for which unique policies are required according to the RDP (Please separate all data types be semicolon, e.g. crystal structures; Protein sequence)",
]

multiple_choice_scores = {
    1: {
        "Research Data Policy (RDP) exists.": 1,
        "Research Data Policy (RDP) does not exists.": 0,
    },
    3: {
        "Data sharing only with editors and referees (no public sharing)": 0,
        "Data sharing encouraged but optional.": 1,
        "Data sharing required but not publicly (e.g. available upon request is allowed).": 2,
        "Public data sharing required only for specific types of data.": 3,
        "Public data sharing of all data required.": 4,
    },
    4: {
        "Public data sharing on a FAIR repository not mentioned in RDP.": 0,
        "Public data sharing on a FAIR repository encouraged.": 1,
        "Public data sharing on a FAIR repository required only for specific types of data (e.g. genetic data has to be shared on a FAIR repository but no other data).": 2,
        "Public data sharing of all data on a FAIR repository required.": 3,
    },
    2: {
        "Not mentioned in the RDP.": 0,
        "Mentioned in the RDP but optional.": 1,
        "Required according to the RDP.": 2,
    },
    5: {
        "No mention of DOIs or other persistent identifiers for datasets or codes.": 0,
        "DOIs or other persistent identifiers recommended for datasets or codes.": 1,
        "DOIs or other persistent identifiers required for datasets or codes.": 2,
    },
    7: {
        "Timing of data availability not addressed in RDP.": 0,
        "Required data must be available prior to review process.": 1,
        "Required data must be available prior to official publication.": 2,
        "Required data must be available after official publication.": 3,
        "Required data must be available after an embargo period.": 4,
    },
    8: {
        "No data sharing method recommended in RDP.": 0,
        "Multiple data sharing methods equally recommended in RDP.": 1,
        "Data is shared upon request to authors in RDP.": 2,
        "Data sharing in supplementary material or hosting by journal recommended in RDP.": 3,
        "Public online repositories recommended in RDP.": 4,
        "Only FAIR repositories recommended in RDP.": 5,
    },
    9: {
        "No mention of data/code licenses in RDP.": 0,
        "Explicit mention of a certain license/license type in RDP.": 1,
        "Open access license required for shared data.": 2,
    },
    10: {
        "Data sharing policy not mentioned in refereeing guidelines.": 0,
        "Data sharing policy mentioned in refereeing guidelines.": 1,
        "Confirmation of shared data or code by referee required.": 2,
        "Additional data or code referee (referee that solely confirms that code and data are shared following the RDP).": 3,
    },
    13: {
        "Code sharing not mentioned.": 0,
        "Code sharing encouraged but optional.": 1,
        "Code sharing required.": 2,
    },
    14: {
        "No mention of dependencies for research code.": 0,
        "Journal policies encourage/recommend stating all dependencies and their versions that were used to run computational experiments.": 1,
        "Journal policies require stating all dependencies and their versions that were used to run computational experiments.": 2,
        "Journal policies require a working container or installation script for code written for computational experiments.": 3,
        "Journal policies require a working container or installation script for code written for computational experiments and a script that reproduces all figures and/or tables in the article.": 4,
    },
    15: {
        "No mention of a persistent identifier or specifying a version of developed code.": 0,
        "Journal policies encourage/recommend a persistent identifier or specifying a version of developed code.": 1,
        "Journal policies require a persistent identifier or specifying a version of developed code.": 2,
    },
    16: {
        "The journal policies do not mention any code quality standards.": 0,
        "The journal policies encourage/recommend certain standards for code.": 1,
        "The journal policies require code of articles to fulfill certain standards.": 2,
        "The journal policies specify criteria for referees to assess the quality of code.": 3,
    },
    17: {
        "No mention of automatic testing to verify code functionality.": 0,
        "The journal policies encourage/recommend automatic testing to verify code functionality.": 1,
        "The journal policies require automatic testing to verify code functionality.": 2,
    },
    18: {
        "No mention of standards for code documentation.": 0,
        "The journal policies encourage/recommend standards for code documentation.": 1,
        "The journal policies require documentation of code.": 2,
    },
    19: {
        "No mention of linting standards for code.": 0,
        "The journal policies encourage/recommend linting standards for code.": 1,
        "The journal policies require certain standards for linting of code.": 2,
    },
    20: {
        "No mention of standards for code development such as continuous integration.": 0,
        "The journal policies encourage/recommend standards for code development such as continuous integration.": 1,
        "The journal policies require standards for code development such as continuous integration.": 2,
    },
}
