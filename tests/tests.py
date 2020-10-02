#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
import tempfile

if __name__ == '__main__' and __package__ is None:
    sys.path.insert( 0, os.path.abspath( os.path.join( os.path.dirname(__file__) , '..' ) ) )

import ratarmount

testData = b"1234567890"
tmpFile = tempfile.TemporaryFile()
tmpFile.write( testData )


print( "Test StenciledFile._findStencil" )
stenciledFile = ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2),(4,4),(1,8),(0,1)] )
expectedResults = [ 0,0, 1,1, 2,2, 3,3,3,3, 4,4,4,4,4,4,4,4, 5 ]
for offset, iExpectedStencil in enumerate( expectedResults ):
    assert stenciledFile._findStencil( offset ) == iExpectedStencil

print( "Test StenciledFile with single stencil" )

assert ratarmount.StenciledFile( tmpFile, [(0,1)] ).read() == b"1"
assert ratarmount.StenciledFile( tmpFile, [(0,2)] ).read() == b"12"
assert ratarmount.StenciledFile( tmpFile, [(0,3)] ).read() == b"123"
assert ratarmount.StenciledFile( tmpFile, [(0,len( testData ) )] ).read() == testData


print( "Test StenciledFile with stencils each sized 1 byte" )

assert ratarmount.StenciledFile( tmpFile, [(0,1),(1,1)] ).read() == b"12"
assert ratarmount.StenciledFile( tmpFile, [(0,1),(2,1)] ).read() == b"13"
assert ratarmount.StenciledFile( tmpFile, [(1,1),(0,1)] ).read() == b"21"
assert ratarmount.StenciledFile( tmpFile, [(0,1),(1,1),(2,1)] ).read() == b"123"
assert ratarmount.StenciledFile( tmpFile, [(1,1),(2,1),(0,1)] ).read() == b"231"

print( "Test StenciledFile with stencils each sized 2 bytes" )

assert ratarmount.StenciledFile( tmpFile, [(0,2),(1,2)] ).read() == b"1223"
assert ratarmount.StenciledFile( tmpFile, [(0,2),(2,2)] ).read() == b"1234"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(0,2)] ).read() == b"2312"
assert ratarmount.StenciledFile( tmpFile, [(0,2),(1,2),(2,2)] ).read() == b"122334"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read() == b"233412"

print( "Test reading a fixed length of the StenciledFile" )

assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 0 ) == b""
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 1 ) == b"2"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 2 ) == b"23"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 3 ) == b"233"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 4 ) == b"2334"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 5 ) == b"23341"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 6 ) == b"233412"
assert ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] ).read( 7 ) == b"233412"

print( "Test seek and tell" )

stenciledFile = ratarmount.StenciledFile( tmpFile, [(1,2),(2,2),(0,2)] )
for i in range( 7 ):
    assert stenciledFile.tell() == i
    stenciledFile.read( 1 )
for i in reversed( range( 6 ) ):
    assert stenciledFile.seek( -1, io.SEEK_CUR ) == i
    assert stenciledFile.tell() == i
assert stenciledFile.seek( 0, io.SEEK_END ) == 6
assert stenciledFile.tell() == 6
assert stenciledFile.seek( 20, io.SEEK_END ) == 26
assert stenciledFile.tell() == 26
assert stenciledFile.read( 1 ) == b""
assert stenciledFile.seek( -6, io.SEEK_END ) == 0
assert stenciledFile.read( 1 ) == b"2"


# JoinedFile

tmpDir = tempfile.TemporaryDirectory()
fileSizes = [2,2,2,4,8,1]
filePaths = [ os.path.join( tmpDir.name, str(i) ) for i in range( len( fileSizes ) ) ]
i = 0
for path, size in zip( filePaths, fileSizes ):
    with open( path, 'wb' ) as file:
        file.write( ''.join( [ chr( i + j ) for j in range( size ) ] ).encode() )
    i += size

print( "Test JoinedFile._findStencil" )
joinedFile = ratarmount.JoinedFile( filePaths )
expectedResults = [ 0,0, 1,1, 2,2, 3,3,3,3, 4,4,4,4,4,4,4,4, 5 ]
for offset, iExpectedStencil in enumerate( expectedResults ):
    assert joinedFile._findStencil( offset ) == iExpectedStencil

print( "Test JoinedFile with single file" )

assert ratarmount.JoinedFile( [ filePaths[0] ] ).read( 1 ) == b"\x00"
assert ratarmount.JoinedFile( [ filePaths[0] ] ).read( 2 ) == b"\x00\x01"
assert ratarmount.JoinedFile( [ filePaths[0] ] ).read() == b"\x00\x01"

print( "Test JoinedFile using two files" )

joinedFile = ratarmount.JoinedFile( filePaths[:2] )
assert joinedFile.read() == b"\x00\x01\x02\x03"
for i in [0,1,2,3,2,1,0,2,0,2]:
    joinedFile.seek( i )
    joinedFile.tell() == i
    assert joinedFile.read( 1 ) == chr( i ).encode()
joinedFile.seek( 0, io.SEEK_END )
assert joinedFile.tell() == 4
