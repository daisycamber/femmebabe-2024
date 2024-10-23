function getBufferAsText(buffer) {
    var s = "";
    for (var t=0; t<buffer.length; t++)
    {
        s += String.fromCharCode(buffer[t]);
    }
    return s;
}

// Author: Alan MacLeod, Sep 2016
(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.Huffman = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){

module.exports = Huffman;

function Huffman()
{
    this._nodes = [];
    this.root = null;
    this._bindict = [];

    this.compress = function(data) // ArrayBuffer
    {
        var view = new Uint8Array(data);

        this._freqAnalysis(view);
        this._buildTree();
        this._buildDictionary('', this.root);

        var numbits = 0;
        for (var t=0; t< view.length; t++)
            numbits += (this._bindict[view[t]][0].length);

        var compressed_size_in_bytes = Math.floor((numbits/8) + 0.5);
        var bw = new BinaryWriter(compressed_size_in_bytes);

        for (var t=0; t<view.length; t++)
            bw.writeBits(this._bindict[view[t]][0]);

        bw.finish();

        var bwtree = new BinaryWriter(4096); // FIXME, can we predict the tree size beforehand?

        this._serialiseNode(this.root, bwtree);

        bwtree.finish(); // VERY IMPORTANT!
        bwtree.prune();

        var headerSize = 8; // two 32-bit vals for tree size (overkill) and original file size
        var catArray = new Uint8Array(bwtree.buffer.byteLength + bw.buffer.byteLength+ headerSize);
        catArray.set(new Uint8Array(bwtree.buffer),0+headerSize);
        catArray.set(new Uint8Array(bw.buffer), bwtree.buffer.byteLength+headerSize);

        var tmp = new Uint32Array(catArray);
        tmp[0] = view.length;
        tmp[1] = bwtree.buffer.byteLength;

        return tmp;
    };

    this.decompress = function(slug)
    {
        var tmp = new Uint32Array(slug);
        var org_size = tmp[0];
        var tree_size = tmp[1];
        var databytes = new Uint8Array(slug);
        var bintree = databytes.subarray(8, 8+tree_size);
        var data = databytes.subarray(8+tree_size);

        var br = new BinaryReader(bintree);
        var tree = this._deserialiseNode(br);

        var binreader = new BinaryReader(data);
        var decoder = new HuffmanDecoder(tree);

        var decompressedArray = new ArrayBuffer(org_size);
        var bview = new Uint8Array(decompressedArray);
        var bviewPtr = 0 ;
        var b;

        while ((b = binreader.readBit()) != null)
        {
            var r = decoder.walk(b);

            if (r)
                bview[bviewPtr++] = r;
        }

        return bview;
    };

    // This method takes a linear bunch of binary and deserialises it into our Huffman tree
    this._deserialiseNode = function(reader)
    {
        var bit = reader.readBit();

        if (bit == 1)
        {   var byte = reader.readByte();
            var n = new Node(byte, null);
            return n;
        } else if (bit == 0) {
            var left = this._deserialiseNode(reader);
            var right = this._deserialiseNode(reader);

            var n = new Node(null, null);
            n.left = left;
            n.right = right;
            return n;
        } else {
            return null;
        }

    };

    // This is a bit clever. Not only serialises the huffman tree, but also compresses it massively!
    // Writes a binary '1' for leaf, '0' for node. Assumes traversal left -> right
    this._serialiseNode = function(node, writer)
    {
        if (node.symbol)
        {
            writer.writeBit(1);
            writer.writeByte(node.symbol);
        } else {
            writer.writeBit(0);
            this._serialiseNode(node.left, writer);
            this._serialiseNode(node.right, writer);
        }
    };

    // Symbol dictionary, has our minimalised binary form for every unique symbol in the source file
    this._buildDictionary = function(binstr, node)
    {
        if (node.symbol)
            this._bindict[node.symbol] = [binstr, node.frequency];

        if (node.right)
            this._buildDictionary(binstr+'1', node.right);

        if (node.left)
            this._buildDictionary(binstr+'0', node.left);
    };

    // After collecting symbols (in .freqAnalysis()) we build the tree from the ground up.
    // First, sort symbols by frequency. Then choose the two lowest and merge them into a new Node
    // Rinse, repeat.
    this._buildTree = function()
    {
        while (this._nodes.length > 1)
        {
            var l = this._nodes.length;
            var a = this._nodes[l-1];
            var b = this._nodes[l-2];

            var n = new Node(null, a.frequency + b.frequency);
            n.left = a;
            n.right = b;

            this._nodes.splice(l-2, 2);
            this._nodes.push(n);

            this._nodes.sort(function(a,b){
                return b.frequency - a.frequency;
            });
        }

        this.root = this._nodes[0];
    };

    this._freqAnalysis = function(view)
    {
        var numSymbols = 0;

        for (var t=0; t<view.length; t++)
        {
            var s = view[t];
            if (!this._nodes[s])
            {
                this._nodes[s] = new Node(s, 1);
                numSymbols++;
            } else {
                this._nodes[s].frequency++;
            }
        }

        this._nodes.sort(function(a,b){
            return b.frequency - a.frequency;
        });

        this._nodes.splice(numSymbols, this._nodes.length - numSymbols);

    }
}

function Node(s, f)
{
    this.symbol = s;
    this.frequency = f;
    this.left = null;
    this.right = null;
}

// When we take our linear binary input stream, we immediately start walking the tree turning left or right if a 0 or 1
// until we arrive at a leaf node, then just return that symbol - and that is how a variable length compressed symbol
// is decoded.
function HuffmanDecoder(root)
{
    this.rootNode = root;
    this.currentNode = null;

    this.walk = function(bin)
    {
        if (!this.currentNode) this.currentNode = this.rootNode;

        if (bin == '0')
            this.currentNode = this.currentNode.left;
        else
            this.currentNode = this.currentNode.right;

        if (this.currentNode.symbol)
        {
            var s = this.currentNode.symbol;
            this.currentNode = this.rootNode;
            return s;

        } else
        {
            return null;
        }
    };

}

// Helper to allow direct manipulation of binary bits
function BinaryReader(buffer)
{
    this.bytes = new Uint8Array(buffer);
    this.bitPosition = 7;
    this.bytePosition = 0;
    this.currentByte = this.bytes[this.bytePosition];


    this._getNextBit = function()
    {
        var bit = (this.currentByte >> this.bitPosition) & 1;

        return !this._moveNextBit() ? null : bit;
    };

    this._moveNextBit = function()
    {
        this.bitPosition--;
        if (this.bitPosition < 0)
        {
            this.bitPosition = 7;
            this.bytePosition++;
            if (this.bytePosition >= this.bytes.length) return false;
            this.currentByte = this.bytes[this.bytePosition];
        }
        return true;
    };

    this.readBit = function()
    {
        return this._getNextBit();
    };

    this.readByte = function()
    {
        var byte = 0;
        for (var t=7; t>=0; t--)
            byte |= (this._getNextBit() << t);

        return byte;
    };

}

function BinaryWriter(maxLength)
{
    this.buffer = new Uint8Array(maxLength);

    this.byteBufferPointer = 0;
    this.currentByte = 0;
    this.bitPointer = 7;

    this.flushByte = function()
    {
        this.buffer[this.byteBufferPointer++] = this.currentByte;
        this.currentByte = 0;
        this.bitPointer = 7;
    };

    this.finish = function()
    {
        if (this.bitPointer != 7)
            this.buffer[this.byteBufferPointer] = this.currentByte;
    };

    this.prune = function()
    {
        this.buffer = this.buffer.slice(0,this.byteBufferPointer+1);
        return this.byteBufferPointer+1;
    };

    this.writeBit = function(bit)
    {
        this.currentByte |= (bit & 1) << this.bitPointer;
        if (--this.bitPointer < 0) this.flushByte();
    };

    this.writeBits = function(bits)
    {
        for (var t= 0,l=bits.length;t<l;t++)
        {
            var bit = parseInt(bits[t]);
            this.writeBit(bit);
        }
    };

    this.writeByte = function(byte)
    {
        var b = byte & 255;
        var bs = "";
        for (var t = 7; t >= 0; t--)
        {
            var bit = ((byte >> t) & 1);
            bs += bit;
            this.writeBit(bit);
        }
    };

    this.writeOutBinary = function()
    {
        var s = "";
        for (var t=0; t<this.buffer.length; t++)
        {
            var byte = this.buffer[t];

            for (var b= 7; b>=0; b--)
            {
                s += ''+((byte>>b)&1)+'';
            }
        };

        return s;
    }
}
},{}]},{},[1])(1)
});

var huffman = new Huffman();
function en(text){
	return huffman.compress(new Uint8Array(text));
}

function de(text) {
	return getBufferAsText(huffman.decompress(text));
}
