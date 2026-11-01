#!/usr/bin/env python3
"""Build only a verified sanitized checkout. Never reads a private vault."""
import pathlib,subprocess,sys,shutil
from check_stage import check
ROOT=pathlib.Path(__file__).resolve().parents[1]
def build(content,output):
 content=pathlib.Path(content).resolve();output=pathlib.Path(output).absolute()
 if output.is_symlink() or output.resolve()!=output or output==ROOT or output in ROOT.parents or output==content or output in content.parents:raise ValueError('unsafe output path')
 if output.exists():shutil.rmtree(output)
 check(content)
 cli=ROOT/'quartz/bootstrap-cli.mjs'
 if not cli.is_file() or not (ROOT/'node_modules').is_dir():raise RuntimeError('Official pinned Quartz and dependencies are not installed; see README')
 return subprocess.run(['node',str(cli),'build','--concurrency','1','-d',str(content),'-o',str(output)],cwd=ROOT,check=True).returncode
if __name__=='__main__':build(sys.argv[1] if len(sys.argv)>1 else ROOT/'content',sys.argv[2] if len(sys.argv)>2 else ROOT/'public')
