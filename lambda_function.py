import json
import boto3

def lambda_handler(event, context):
    """
    AWS Lambda Backend for SSM Patch Compliance Light Board
    Evaluates fleet-wide patch status and computes the 3-LED indicator state:
      - GREEN: All managed instances are 100% compliant (0 missing, 0 pending reboot)
      - YELLOW: Instances pending reboot or scan
      - RED: Instances missing critical or security patches
    """
    ssm = boto3.client('ssm')
    
    try:
        # 1. Retrieve all managed instances registered with Systems Manager
        inst_resp = ssm.describe_instance_information()
        instances = inst_resp.get('InstanceInformationList', [])
        
        if not instances:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'led_state': 'OFF',
                    'summary': {'total': 0, 'compliant': 0, 'pending': 0, 'non_compliant': 0},
                    'instances': []
                })
            }
        
        instance_ids = [i['InstanceId'] for i in instances]
        
        # 2. Query patch compliance states from SSM Patch Manager
        patch_resp = ssm.describe_instance_patch_states(InstanceIds=instance_ids)
        patch_states = {s['InstanceId']: s for s in patch_resp.get('InstancePatchStates', [])}
        
        fleet_details = []
        non_compliant_count = 0
        pending_count = 0
        compliant_count = 0
        
        for inst in instances:
            iid = inst['InstanceId']
            state = patch_states.get(iid, {})
            missing = state.get('MissingCount', 0)
            pending_reboot = state.get('InstalledPendingRebootCount', 0)
            installed = state.get('InstalledCount', 0)
            
            # Determine individual instance health
            if missing > 0:
                inst_status = "NON_COMPLIANT"
                non_compliant_count += 1
            elif pending_reboot > 0:
                inst_status = "PENDING_REBOOT"
                pending_count += 1
            elif installed > 0:
                inst_status = "COMPLIANT"
                compliant_count += 1
            else:
                inst_status = "PENDING_SCAN"
                pending_count += 1
                
            fleet_details.append({
                'instance_id': iid,
                'os': f"{inst.get('PlatformName', 'Linux')} {inst.get('PlatformVersion', '')}",
                'status': inst_status,
                'missing_patches': missing,
                'installed_patches': installed,
                'pending_reboot': pending_reboot,
                'last_scan': str(state.get('OperationEndTime', 'Never'))
            })
            
        # 3. Compute 3-LED Panel Status Logic
        if non_compliant_count > 0:
            overall_led = "RED"
        elif pending_count > 0:
            overall_led = "YELLOW"
        else:
            overall_led = "GREEN"
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'led_state': overall_led,
                'summary': {
                    'total': len(instances),
                    'compliant': compliant_count,
                    'pending': pending_count,
                    'non_compliant': non_compliant_count
                },
                'instances': fleet_details
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
