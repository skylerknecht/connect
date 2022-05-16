import argparse

from connect.convert import string_to_base64, bytes_to_base64
from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category, Cmd


@with_default_category('Files')
class FilesCommands(CommandSet):
    """
    The STDApi command set.
    """

    def __init__(self, post_job):
        super().__init__()
        self.post_job = post_job

    """ 
    DelFile Command 
    """

    del_file_parser = Cmd2ArgumentParser()
    del_file_parser.add_argument('file', help='the file to delete')

    @with_argparser(del_file_parser)
    def do_delfile(self, args: argparse.Namespace):
        """ List the contents and properties of a directory. """
        file = string_to_base64(args.file)
        self.post_job(f'"name":"delfile","arguments":"{file}","type":1')

    """ 
    Download Command 
    """

    download_parser = Cmd2ArgumentParser()
    download_parser.add_argument('file', help='the file to download')

    @with_argparser(download_parser)
    def do_download(self, args: argparse.Namespace):
        """ Download a remote file. """
        file = string_to_base64(args.file)
        self.post_job(f'"name":"download","arguments":"{file}","type":2')

    """
    Upload Command
    """

    upload_parser = Cmd2ArgumentParser()
    upload_parser.add_argument('file', completer=Cmd.path_complete, help='file to upload')
    upload_parser.add_argument('path', help='path to upload to')

    @with_argparser(upload_parser)
    def do_upload(self, args: argparse.Namespace):
        """ Uploads a file to the remote machine. """
        with open(args.file, 'rb') as fd:
            file = bytes_to_base64(fd.read())
        path = string_to_base64(args.path)
        self.post_job(f'"name":"upload","arguments":"{file},{path}","type":1')