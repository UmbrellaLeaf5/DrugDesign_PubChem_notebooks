import requests
import os
import time

sleepSecs = 0.2

compoundsLink = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/JSON?heading=Acute+Effects&page={page}"
tableLink = 'https://pubchem.ncbi.nlm.nih.gov/sdq/sdqagent.cgi?infmt=json&outfmt=xml&query={{"download":"*","collection":"{collection}","order":["relevancescore,desc"],"start":1,"limit":10000000,"downloadfilename":"{fileName}","where":{{"ands":[{{"sid":"{sid}"}}]}}}}'

# всего 113 страниц так что endPage ставить больше 114 не стоит
startPage = -1
endPage = -1
curPage = startPage
while curPage < endPage:
    curDir = f"./page_{curPage}"
    if not os.path.exists(curDir):
        os.makedirs(curDir)

    compoundsList = requests.get(compoundsLink.format(page=curPage))
    data = compoundsList.json()["Annotations"]

    if curPage > int(data["TotalPages"]):
        print("Invalid page, exiting")
        exit(1)

    for index, compound in enumerate(data["Annotation"]):
        try:
            cid = compound["LinkedRecords"]["CID"][0]
            filename = f"{curDir}/{cid}"

            if os.path.exists(filename):
                print(f"Skipping existing file {filename}")
                continue

            tableInfoRaw = compound["Data"][0]["Value"]["ExternalTableName"]
            tableInfo = {}
            for keyValue in tableInfoRaw.split("&"):
                key, value = keyValue.split("=")
                tableInfo[key] = value
            if tableInfo["query_type"] != "sid":
                print(f"Unknown query type on compound number {index} page {curPage} ")

            acuteEffects = requests.get(
                tableLink.format(
                    collection=tableInfo["collection"],
                    fileName=tableInfo["query"],
                    sid=int(tableInfo["query"]),
                )
            )

            with open(filename, "wb") as file:
                file.write(acuteEffects.content)
        except Exception as e:
            print(f"Failed at index {index} of page {curPage} with exception:")
            print(e)
        time.sleep(sleepSecs)

    curPage += 1
