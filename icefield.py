import os
import sys
import datetime
import logging
import json
import time

import boto
from boto.glacier.concurrent import ConcurrentDownloader
import aaargh

ICEFIELD_DOMAIN = 'icefield-domain'

app = aaargh.App(description="Manage backups with Amazon Glacier")

log = logging.getLogger(__name__)
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class SimpleDB(object):
    """
    Class for managing Glacier vault and archive metadata
    """
    def __init__(self):
        self.connection = boto.connect_sdb()
        self.domain = self.connection.create_domain(ICEFIELD_DOMAIN)
    
    def add_archive(self, archiveid, description, size, vault, creationdate=None):
        if creationdate is None:
            creationdate = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        attributes = {'ArchiveDescription': description, 'Vault':vault, 
                      'Size': size, 'CreationDate': creationdate}
        self.domain.put_attributes(archiveid, attributes)

    def list_archives(self, vault=None):
        if vault is None:
            query = 'SELECT * FROM `{}`'.format(ICEFIELD_DOMAIN)
        else:
            query = 'SELECT * FROM `{}` WHERE Vault="{}"'.format(ICEFIELD_DOMAIN, vault)
        result = self.domain.select(query, next_token=None, consistent_read=False, max_items=None)
        r = [dict([('ArchiveId', a.name)]+a.items()) for a in result]
        return json.dumps(r, sort_keys=True, indent=4)

class GlacierBackend(object):
    """
    Backend to handle Glacier upload/download
    """
    def __init__(self, vault_name):
        con = boto.connect_glacier()
        self.vault = con.create_vault(vault_name)

    def upload(self, filename, description=None):
        if description is None:
            description = os.path.basename(filename)
        archive_id = self.vault.concurrent_create_archive_from_file(filename, description)
        return archive_id

    def retrieve_inventory(self, jobid):
        """
        Initiate a job to retrieve Galcier inventory or output inventory
        """
        if jobid is None:
            return self.vault.retrieve_inventory(sns_topic=None, description="Icefield inventory job")
        else:
            return self.vault.get_job(jobid)

    def retrieve_archive(self, archive_id, jobid):
        """
        Initiate a job to retrieve Galcier archive or download archive
        """
        if jobid is None:
            return self.vault.retrieve_archive(archive_id, sns_topic=None, description='Retrieval job')
        else:
            return self.vault.get_job(jobid)


@app.cmd(help="List vaults")
def list_vaults():
    connection = boto.connect_glacier()
    print('\n'.join([vault.name for vault in connection.list_vaults()]))

@app.cmd(help="List archives in SimpleDB inventory")
@app.cmd_arg('-v', '--vault', help="Glacier vault")
def list_archives(vault=None):
    sdb = SimpleDB()
    print sdb.list_archives(vault)

@app.cmd(help="Upload a file")
@app.cmd_arg('-f', '--filename', required=True)
@app.cmd_arg('-v', '--vault', required=True, help="Glacier vault")
def upload(filename, vault):
    description = os.path.basename(filename)
    glacier_backend = GlacierBackend(vault)
    log.info("Uploading {} to vault {}".format(filename, vault))
    start = time.time()
    archive_id = glacier_backend.upload(filename, description)
    log.info("Finished uploading {} to vault {} ({:.0f} secs)".format(filename, vault, time.time()-start))
    
    # Update inventory
    size = os.path.getsize(filename)
    sdb = SimpleDB()
    sdb.add_archive(archive_id, description, size, vault)
    log.info("Updated inventory on SimpleDB")
    

@app.cmd(help="Retrieve Glacier inventory")
@app.cmd_arg('-j', '--jobid', type=str, default=None, help="inventory job id")
@app.cmd_arg('-v', '--vault', required=True, help="Glacier vault")
def retrieve_inventory(vault, jobid=None):
    glacier_backend = GlacierBackend(vault)
    job = glacier_backend.retrieve_inventory(jobid)
    if jobid is not None:
        print json.dumps(job.get_output())


@app.cmd(help="Retrieve Glacier archive")
@app.cmd_arg('archiveid', help="archive id")
@app.cmd_arg('-j', '--jobid', type=str, default=None, help="archive retrieval job id")
@app.cmd_arg('-v', '--vault', required=True, help="Glacier vault")
def retrieve_archive(archiveid, vault, jobid=None):
    glacier_backend = GlacierBackend(vault)
    job = glacier_backend.retrieve_archive(archiveid, jobid)
    if jobid is not None:
        cd = ConcurrentDownloader(job, part_size=4194304, num_threads=8)
        cd.download(archiveid[:8]+'.out')


def main():
    app.run()

if __name__ == '__main__':
    main()
