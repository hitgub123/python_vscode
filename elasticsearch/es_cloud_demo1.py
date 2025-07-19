from elasticsearch import Elasticsearch, helpers
import es_cloud_util,gemini_api_util

if __name__ == "__main__":
    dims=768
    client = Elasticsearch(
        "https://my-elasticsearch-project-a6634e.es.us-east-1.aws.elastic.cloud:443",
        api_key="V1BWMEZwZ0I5UE5nM2tDY3pXS0o6cUxkV1ZMYVlxUEZiMEpaZ3N3em9UQQ==",
    )
    # index_name = "search-cec4"
    index_name = "search-xntd"

    #########update_mapping########
    # es_cloud_util.update_mapping(client, index_name,dims=dims)

    #########update_index########
    # docs = [ "text": "Yellowstone", "vector": [ 7.051, 3.335,  5.163 ] } ]
    # es_cloud_util.update_index(client,docs, index_name)
    chunks = [
        "Yellowstone National Park is one of the largest national parks in the United States. It ranges from the Wyoming to Montana and Idaho, and contains an area of 2,219,791 acress across three different states. Its most famous for hosting the geyser Old Faithful and is centered on the Yellowstone Caldera, the largest super volcano on the American continent. Yellowstone is host to hundreds of species of animal, many of which are endangered or threatened. Most notably, it contains free-ranging herds of bison and elk, alongside bears, cougars and wolves. The national park receives over 4.5 million visitors annually and is a UNESCO World Heritage Site.",
        "Yosemite National Park is a United States National Park, covering over 750,000 acres of land in California. A UNESCO World Heritage Site, the park is best known for its granite cliffs, waterfalls and giant sequoia trees. Yosemite hosts over four million visitors in most years, with a peak of five million visitors in 2016. The park is home to a diverse range of wildlife, including mule deer, black bears, and the endangered Sierra Nevada bighorn sheep. The park has 1,200 square miles of wilderness, and is a popular destination for rock climbers, with over 3,000 feet of vertical granite to climb. Its most famous and cliff is the El Capitan, a 3,000 feet monolith along its tallest face.",
        "Rocky Mountain National Park  is one of the most popular national parks in the United States. It receives over 4.5 million visitors annually, and is known for its mountainous terrain, including Longs Peak, which is the highest peak in the park. The park is home to a variety of wildlife, including elk, mule deer, moose, and bighorn sheep. The park is also home to a variety of ecosystems, including montane, subalpine, and alpine tundra. The park is a popular destination for hiking, camping, and wildlife viewing, and is a UNESCO World Heritage Site."
    ]
    vectors=gemini_api_util.get_embedings(chunks,dims)
    docs = [{"text": chunks[i], "vector": vectors[i].values} for i in range(len(chunks))]
    es_cloud_util.update_index(client, docs,index_name)

    #########query########
    # query_kw = "please give me introduction of Yellowstone park"
    # query_embedding=gemini_api_util.get_embedings(query_kw)[0].values
    # print(query_embedding)
    # es_cloud_util.query(client,index_name, query_embedding)
