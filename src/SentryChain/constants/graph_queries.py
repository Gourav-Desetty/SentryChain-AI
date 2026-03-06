SUPPLIER_CONTRACT = """
            MERGE (s:Supplier {name: $s_name})
            MERGE (c:Contract {id: $c_id})
            MERGE (s)-[:HAS_CONTRACT]->(c)
            SET c.last_updated = timestamp()
            """

PENALTY_NODES = """
        MATCH (c:Contract {id: $c_id})
        MERGE (pc:PenaltyRule {id: $p_uid})
        SET pc.type = $type, 
            pc.trigger = $trigger, 
            pc.amount = $amount,
            pc.clause_ref = $ref
        MERGE (c)-[:ENFORCES_PENALTY]->(pc)
        """

CONTRACT_CHUNK_LINK = """
        MATCH (c:Contract {id: $c_id})
        MERGE (ch:Chunk {vector_id: $v_id})
        SET ch.text_preview = $text
        MERGE (c)-[:HAS_CONTENT_CHUNK]->(ch)
        """