/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<8>  PROTOCOL_ICMP = 0x01;
const bit<8>  PROTOCOL_TCP = 0x06;
const bit<8>  PROTOCOL_UDP = 0x11;
const bit<16> TYPE_IPV4 = 0x800;
const bit<5>  IPV4_OPTION_MRI = 31;

#define MAX_HOPS 9

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> switchID_t;
typedef bit<32> qdepth_t;
typedef bit<32> qtime_t;
typedef bit<32> ingress_ts_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    // bit<8>    diffserv;
    bit<6>    dscp;
    bit<2>    ecn;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}
header icmp_t {
    bit<8> type;
    bit<8> subtype;
    bit<16> checksum;
    bit<32> variable;

}

header ipv4_option_t {
    bit<1> copyFlag;
    bit<2> optClass;
    bit<5> option;
    bit<8> optionLength;
}

header mri_t {
    bit<16>  count;
    // bit<16>  debug;
}

header switch_t {
    switchID_t  swid;
    qdepth_t    qdepth;
    ingress_ts_t ingress_ts;
    qtime_t qtime;
}

struct ingress_metadata_t {
    bit<16>  count;
}

struct parser_metadata_t {
    bit<16>  remaining;
    bit<1>  cloneable;
}

struct metadata {
    ingress_metadata_t   ingress_metadata;
    parser_metadata_t   parser_metadata;
}

struct headers {
    ethernet_t         ethernet;
    ipv4_t             ipv4;
    ipv4_option_t      ipv4_option;
    // icmp_t             icmp;
    mri_t              mri;
    switch_t[MAX_HOPS] swtraces;
}

error { IPHeaderTooShort }

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4_protocol;
            default: accept;
        }
    }

    state parse_ipv4_protocol {
        // log_msg("parse_ipv4");
        packet.extract(hdr.ipv4);

        transition select(hdr.ipv4.protocol){
            // PROTOCOL_ICMP: parse_icmp;
            PROTOCOL_TCP: parse_tcp;
            PROTOCOL_UDP: parse_udp;
            default: accept;
        }


    }

    state parse_ipv4_ihl {

        verify(hdr.ipv4.ihl >= 5, error.IPHeaderTooShort);
        transition select(hdr.ipv4.ihl) {
            5             : accept;
            default       : parse_ipv4_option;
        }
    }

    state parse_ipv4_option {
        // log_msg("parse_ipv4_option");
        meta.parser_metadata.cloneable = 1;
        packet.extract(hdr.ipv4_option);
        transition select(hdr.ipv4_option.option) {
            IPV4_OPTION_MRI: parse_mri;
            default: accept;
        }
    }

    state parse_mri {
        // log_msg("parse_mri");
        packet.extract(hdr.mri);
        meta.parser_metadata.remaining = hdr.mri.count;

        transition select(meta.parser_metadata.remaining) {
            0 : accept;
            default: parse_swtrace;
        }
    }

    state parse_swtrace {
        // log_msg("parse_swtrace");
        packet.extract(hdr.swtraces.next);
        meta.parser_metadata.remaining = meta.parser_metadata.remaining  - 1;
        transition select(meta.parser_metadata.remaining) {
            0 : accept;
            default: parse_swtrace;
        }
    }

    // state parse_icmp{
    //     packet.extract(hdr.icmp);
    //     transition parse_ipv4_ihl;
    // }

    state parse_tcp{
        transition parse_ipv4_ihl;
    }

    state parse_udp{
        transition parse_ipv4_ihl;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action do_clone(ip4Addr_t sinkAddr) {
        ip4Addr_t temp = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = (ip4Addr_t) sinkAddr;
        clone_preserving_field_list(CloneType.I2E, (bit<32>)99, (bit<8>)1);
        hdr.mri.setInvalid();
        hdr.swtraces[0].setInvalid();
        hdr.swtraces[1].setInvalid();
        hdr.swtraces[2].setInvalid();
        hdr.swtraces[3].setInvalid();
        hdr.swtraces[4].setInvalid();
        hdr.swtraces[5].setInvalid();
        hdr.swtraces[6].setInvalid();
        hdr.swtraces[7].setInvalid();
        hdr.swtraces[8].setInvalid();
        hdr.ipv4.ihl = (bit<4>) 5;
        hdr.ipv4_option.setInvalid();
        hdr.ipv4.dstAddr = temp; //maybe also set mac?

        // test if this works properly that the clone is instant. 
    }

     
    table last_hop {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            do_clone;
            NoAction;
        }
        size = 64;
        default_action = NoAction();
    }


    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }



    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();

            if( meta.parser_metadata.cloneable == 1 ){
                last_hop.apply();
            }
           
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {                
    action add_swtrace(switchID_t swid, bit<32> ecn_threshold) {
        // log_msg("add_swtrace");
        hdr.mri.count = hdr.mri.count + 1;
        hdr.swtraces.push_front(1);
        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = swid;
        hdr.swtraces[0].qdepth = (qdepth_t)standard_metadata.deq_qdepth;
        hdr.swtraces[0].ingress_ts = (ingress_ts_t)standard_metadata.ingress_global_timestamp;
        hdr.swtraces[0].qtime      = (qtime_t)standard_metadata.deq_timedelta;


        hdr.ipv4.ihl = hdr.ipv4.ihl + 4;
        hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 16;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16;

        if (standard_metadata.deq_timedelta > ecn_threshold) {
            hdr.ipv4.ecn = 0x03;
        }
    }

    table swtrace {
        actions = {
            add_swtrace;
            NoAction;
        }
        default_action = NoAction();
    }

    apply {
        if (hdr.mri.isValid()) {
            swtrace.apply();
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.dscp,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv4_option);
        packet.emit(hdr.mri);
        packet.emit(hdr.swtraces);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
