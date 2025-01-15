# All agent development
The starting place for development for all agents

AWS Notes to incorporate -
https://aws.amazon.com/blogs/compute/query-for-the-latest-amazon-linux-ami-ids-using-aws-systems-manager-parameter-store/ -

#Scripts I use when instance is started. This should be not for automating AMI's but for automating based on suite of tooling for AL2023, ubuntu, fedora, etc.

Always update packages... test everything..
## Grab docs 
When instance is started.. use this for memory or RAG..
Docs.. to parse..
Version checking.. testing..

#Script info
sudo ln -sf /usr/bin/python3.9 /usr/bin/python

AWS Admin Agent.
Being able to run tooling.. get docs.. 
https://docs.aws.amazon.com/zh_cn/cli/latest/reference/trustedadvisor/index.html


## Spin up MongoDB Atlas local cluster
install mongosh via brew 
docker-compose up -d
mongosh "mongodb://user:pass@localhost:27018/?directConnection=true"
show dbs
use <db name>
show collections
## Check embeddings
db.collectionName.find()