/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<8>  PROTOCOL_ICMP = 0x01;
const bit<8>  PROTOCOL_TCP = 0x07;
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

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
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
}

struct ingress_metadata_t {
    bit<16>  count;
}

struct parser_metadata_t {
    bit<16>  remaining;
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
        log_msg("parse_ipv4_option");
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

        // clone(CloneType.I2E,1,(bit<32>)1);       
        // clone(CloneType.I2E,(bit<32>)99);       
        clone_preserving_field_list(CloneType.I2E,(bit<32>)99,(bit<8>)1);       
        // extern void clone(in CloneType type, in bit<32> session);
        // extern void clone_preserving_field_list(in CloneType type, in bit<32> session, bit<8> index);
// 
        // log_msg("ipv4_forward");
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
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    action add_swtrace(switchID_t swid) {
        log_msg("add_swtrace");
        hdr.mri.count = hdr.mri.count + 1;
        hdr.swtraces.push_front(1);
        // According to the P4_16 spec, pushed elements are invalid, so we need
        // to call setValid(). Older bmv2 versions would mark the new header(s)
        // valid automatically (P4_14 behavior), but starting with version 1.11,
        // bmv2 conforms with the P4_16 spec.
        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = swid;
        hdr.swtraces[0].qdepth = (qdepth_t)standard_metadata.deq_qdepth;

        hdr.ipv4.ihl = hdr.ipv4.ihl + 2;
        hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 8;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 8;
    }

    table swtrace {
        actions = {
            add_swtrace;
            NoAction;
        }
        default_action = NoAction();
    }

    // register<bit<32>>(128) myReg;


    apply {

        // if (standard_metadata.i)

        if (hdr.ipv4.isValid()){
        log_msg("my standard_metadata.instance_type={}",{standard_metadata.instance_type});
                    if (standard_metadata.instance_type == 0){
                        log_msg("PKT_INSTANCE_TYPE_INGRESS_CLONE found!");
                        standard_metadata.egress_port = 3;
                    }
        }
      

       

        if (hdr.mri.isValid()) {
            // log_msg("mri is valid");
            swtrace.apply();
            // bit<32> regID = 0;
            // bit<32> regVal = 0;
            // log_msg("before_regVal={}",{regVal});
            // myReg.read(regVal, (bit<32>)regID);
            // log_msg("after_regVal={}",{regVal});
            // myReg.write((bit<32>)regID, (bit<32>)regVal+1);

            // if (regVal > 10){
                // log_msg("regVal={} is over 10",{regVal});
                // hdr.ipv4.protocol = (bit<8>) 88;
            // }

            // if (regVal % 2 == 0){
                // log_msg("regVal={} is even",{regVal});
                // hdr.ipv4.protocol = (bit<8>) 88;
            // }
        }

        // hdr.ipv4_option.setValid();
        // hdr.mri.setValid();
        // hdr.ipv4.setValid();
        // hdr.ipv4.ihl = (bit<4>) 6;
        // hdr.ipv4.ttl = (bit<8>) 8;
        // hdr.ipv4.totalLen = hdr.ipv4.totalLen + 32;//16;
        // hdr.ipv4.totalLen = hdr.ipv4.totalLen + 32;//16;
        // hdr.ipv4.totalLen = hdr.ipv4.totalLen -4 ;//16;
        // log_msg("hdr.ipv4_option");
        

       

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
              hdr.ipv4.diffserv,
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


        // update_checksum(hdr.icmp.isValid(), {hdr.icmp.type,hdr.icmp.subtype,hdr.icmp.variable},hdr.icmp.checksum, HashAlgorithm.csum16);
        // Checksum: 0x3d6a incorrect, should be 0x0729
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
