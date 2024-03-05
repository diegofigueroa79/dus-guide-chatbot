from langchain.schema.document import Document
import re

class DUSGuideSplitter:
    def __init__(self):
        self.section_regex = "\s\sSection\s[0-9][0-9][0-9]\s\s"
        self.subsection_regex = "\s\s[0-9][0-9][0-9][.][0-9][0-9]\s\s"
        self.glossary_regex = "\s\sGlossary\s"
        self.footer_regex = "\s\s©\s20[0-9][0-9]\sFannie\sMae[.]\sTrademarks\sof\sFannie\sMae[.]\s\sEffective:\s[0-9][0-9]/[0-9][0-9]/20[0-9][0-9]\s\s([0-9]|[0-9][0-9])\sof\s[0-9][0-9]"
    
    def split_documents(self, documents):
        docs = []
        
        for document in documents:
            part, chapter = self.extract_part_and_chapter(document)
            document.metadata["part"] = part
            document.metadata["chapter"] = chapter
            sections = self.extract_subsection(document, self.section_regex)
            subsections = None
            for section in sections:
                subsections = self.extract_subsection(section, self.subsection_regex)
                if subsections:
                    glossary = self.extract_glossary(subsections[-1], self.glossary_regex)
                    if glossary:
                        subsections.pop(-1)
                        subsections += glossary
                    docs += subsections
                else:
                    glossary = self.extract_glossary(section, self.glossary_regex)
                    if glossary:
                        docs += glossary
                    else:
                        docs.append(section)
        return docs
                
    
    def extract_subsection(self, document, regex):
        content = document.page_content
        content = self.clean(content)
        subsections = []
        
        subsection_strs = re.findall(regex, content)
        subsection_locs = []
        for subsection in subsection_strs:
            match = re.search(subsection, content)
            subsection_locs.append(match.span())
        
        for i, span in enumerate(subsection_locs):
            try:
                subsections.append(
                    Document(
                        page_content=content[span[0]:subsection_locs[i+1][0]],
                        metadata={"source": document.metadata['source'], "part": document.metadata['part'], "chapter": document.metadata['chapter']}
                    )
                )
            except:
                subsections.append(
                    Document(
                        page_content=content[span[0]:],
                        metadata={"source": document.metadata['source'], "part": document.metadata['part'], "chapter": document.metadata['chapter']}
                    )
                )
        return subsections
    
    def extract_glossary(self, document, regex):
        content = document.page_content
        
        match = re.search(regex, content)
        
        if match:
            section = Document(
                page_content=content[:match.span()[0]],
                metadata={"source": document.metadata['source'], "part": document.metadata['part'], "chapter": document.metadata['chapter']}
            )
            glossary = Document(
                page_content=content[match.span()[0]:],
                metadata={"source": document.metadata['source'], "part": document.metadata['part'], "chapter": document.metadata['chapter']}
            )
            return [section, glossary]
        else:
            return False

    def clean(self, content):
        content = re.sub(self.footer_regex, "", content)
        return content
    
    def extract_part_and_chapter(self, document):
        content = document.page_content
        source = document.metadata["source"]
        part = re.search("Part [a-zA-Z]", content).group()
        chapter = re.search("Chapter [0-9]", content).group()
        return part, chapter


class DUSUpdateSplitter:
    def extract_chunks:
        pass
    
    def extract_part_and_chapter:
        pass
    
    def extract_effective_date:
        pass