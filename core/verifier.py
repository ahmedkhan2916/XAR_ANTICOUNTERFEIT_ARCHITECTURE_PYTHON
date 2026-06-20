# core/verifier.py


from core.virtual_color import VirtualColorMapper
from security.signature import SignatureEngine
from core.pattern_engine import PatternEngine


class Verifier:

    """
    End-to-end verification engine:
    - Rebuilds virtual colors
    - Reconstructs pattern
    - Regenerates pattern hash
    - Verifies signature
    """

    def __init__(self,secret_key:str, matrix_size:int=5):
        self.secret_key = secret_key
        self.mapper = VirtualColorMapper(secret_key)
        self.pattern_engine = PatternEngine(matrix_size)
        self.signature_engine = SignatureEngine(secret_key)

    def verify(self,binary_data:str,context:str,signature:str)->dict:

     try:  
        #Step1 encode data again (rebuild same transformation):
        encode_result=self.mapper.encode(binary_data,context)

        colors= encode_result["colors"]
        mapping=encode_result["mapping"]

        #Step2 Rebuild Matrix:
        matrix=self.pattern_engine.generate_matrix(colors)

        #Step3 Validate Pattern Rules:
        valid,issues=self.pattern_engine.validate_pattern(matrix)

        #Step4 Generate Pattern Hash:
        pattern_hash=self.pattern_engine.generate_pattern_hash(matrix)

        #Step5 verify Signature:
        signature_valid=self.signature_engine.verify_signature(binary_data,pattern_hash,context,signature)

        #Step6 Final Result:

        final_result=valid and signature_valid

        return {
                "final_result": final_result,
                "pattern_valid": valid,
                "signature_valid": signature_valid,
                "issues": issues,
                "pattern_hash": pattern_hash,
                "colors": colors,
                "mapping": mapping
            }

     except Exception as e:
           
            return {
                "final_result": False,
                "error": str(e)
            }
        
    
