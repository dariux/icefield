import os
import sys
from datetime import datetime
import logging
import json
import time

import boto
from boto.glacier.concurrent import ConcurrentDownloader
import aaargh


app = aaargh.App(description="Manage backups with Amazon Glacier")

log = logging.getLogger(__name__)
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class GlacierBackend:
    """
    Backend to handle Glacier upload/download
    """
    def __init__(self, vault_name):
        con = boto.connect_glacier()
        self.vault = con.create_vault(vault_name)
        self.container = "Glacier vault: {}".format(vault_name)

    def upload(self, filename, description=None):
        if description is None:
            description = os.path.basename(filename)
        archive_id = self.vault.concurrent_create_archive_from_file(filename, description)

    def retrieve_inventory(self, jobid):
        """
        Initiate a job to retrieve Galcier inventory or output inventory
        """
        if jobid is None:
            return self.vault.retrieve_inventory(sns_topic=None, description="Bakthat inventory job")
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

@app.cmd(help="Upload a file")
@app.cmd_arg('-f', '--filename')
@app.cmd_arg('-v', '--vault', help="Glacier vault")
def upload(filename, vault):
    description = os.path.basename(filename)
    glacier_backend = GlacierBackend(vault)
    log.info("Uploading {} to vault {}".format(filename, vault))
    start = time.time()
    glacier_backend.upload(filename, description)
    log.info("Finished uploading {} to vault {} ({} secs)".format(filename, vault, time.time()-start))

@app.cmd(help="Retrieve Glacier inventory")
@app.cmd_arg('-j', '--jobid', type=str, default=None, help="inventory job id")
@app.cmd_arg('-v', '--vault', help="Glacier vault")
def retrieve_inventory(vault, jobid=None):
    glacier_backend = GlacierBackend(vault_name)
    job = glacier_backend.retrieve_inventory(jobid)
    if jobid is not None:
        print json.dumps(job.get_output())


@app.cmd(help="Retrieve Glacier archive")
@app.cmd_arg('archiveid', help="archive id")
@app.cmd_arg('-j', '--jobid', type=str, default=None, help="archive retrieval job id")
@app.cmd_arg('-v', '--vault', help="Glacier vault")
def retrieve_archive(archiveid, vault, jobid=None):
    glacier_backend = GlacierBackend(vault_name)
    job = glacier_backend.retrieve_archive(archiveid, jobid)
    if jobid is not None:
        cd = ConcurrentDownloader(job, part_size=4194304, num_threads=8)
        cd.download(archiveid[:8]+'.out')


def main():
    app.run()

if __name__ == '__main__':
    main()
