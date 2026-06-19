using UnityEngine;
using UnityEngine.InputSystem;

public class CameraFollow : MonoBehaviour
{
    [Header("Target")]
    public Transform target;          
    public Transform cameraTarget;    

    [Header("Orbit")]
    public float mouseSensitivity = 2f;
    public float yawAngle   = 0f;     
    public float pitchAngle = 20f;    

    [Header("Pitch Limits")]
    public float minPitch = -10f;
    public float maxPitch =  70f;

    [Header("Distance & Height")]
    public float distance = 8f;

    [Header("Smoothing")]
    public float positionSmooth = 8f;
    public float rotationSmooth = 10f;

    // Input
    InputAction lookAction;

    void Start()
    {
        lookAction = InputSystem.actions.FindAction("Look");

        
        Vector3 angles = transform.eulerAngles;
        yawAngle   = angles.y;
        pitchAngle = angles.x;

        Cursor.lockState = CursorLockMode.Locked;
    }

    void LateUpdate()
    {
        if (target == null) return;

        HandleOrbitInput();
        ApplyCameraTransform();
        UpdateCameraTargetForward();
    }

    // Input

    void HandleOrbitInput()
    {
        if (Cursor.lockState != CursorLockMode.Locked) return;

        Vector2 look = lookAction.ReadValue<Vector2>();

        yawAngle   += look.x * mouseSensitivity;
        pitchAngle -= look.y * mouseSensitivity; // subtract so mouse-up = camera-up
        pitchAngle  = Mathf.Clamp(pitchAngle, minPitch, maxPitch);
    }

    // Canera

    void ApplyCameraTransform()
    {
        
        Quaternion desiredRot = Quaternion.Euler(pitchAngle, yawAngle, 0f);

        
        Vector3 desiredPos = target.position - desiredRot * Vector3.forward * distance;

        
        transform.position = Vector3.Lerp(
            transform.position,
            desiredPos,
            positionSmooth * Time.deltaTime
        );

        transform.rotation = Quaternion.Slerp(
            transform.rotation,
            desiredRot,
            rotationSmooth * Time.deltaTime
        );
    }

    // Camera Target
    void UpdateCameraTargetForward()
    {
        if (cameraTarget == null) return;

        cameraTarget.position = target.position;
        cameraTarget.rotation = Quaternion.Euler(0f, yawAngle, 0f);
    }

    
    void OnDrawGizmosSelected()
    {
        if (target == null) return;
        Gizmos.color = Color.cyan;
        Gizmos.DrawLine(target.position, transform.position);
        Gizmos.DrawWireSphere(target.position, 0.3f);
    }
}