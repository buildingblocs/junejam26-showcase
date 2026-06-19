using UnityEngine;
using UnityEngine.InputSystem;

public class SoapController : MonoBehaviour
{
    [Header("References")]
    public Transform cameraTarget; 

    [Header("Movement")]
    public float moveSpeed = 18f;
    public float maxSpeed = 12f;

    [Header("Jump")]
    public float jumpForce = 9f;
    public LayerMask groundLayer;
    public float groundCheckRadius = 0.35f;

    
    InputAction moveAction;
    InputAction jumpAction;

    
    Rigidbody rb;

    
    private float moveX;
    private float moveZ;

    
    private bool jumpQueued;
    private bool isGrounded;

    void Start()
    {
        rb = GetComponent<Rigidbody>();

        if (rb == null)
            Debug.LogError("SoapController: Missing Rigidbody component.");

        moveAction = InputSystem.actions.FindAction("Move");
        jumpAction = InputSystem.actions.FindAction("Jump");

        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        HandleCursorLock();
        ReadMovementInput();
        QueueJump();
    }

    void FixedUpdate()
    {
        CheckGrounded();
        ApplyMovement();
        ClampHorizontalSpeed();
        ApplyJump();
    }

    // Input

    void HandleCursorLock()
    {
        if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame)
            Cursor.lockState = CursorLockMode.Locked;

        if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
            Cursor.lockState = CursorLockMode.None;
    }

    void ReadMovementInput()
    {
        Vector2 moveValue = moveAction.ReadValue<Vector2>();
        moveX = moveValue.x;
        moveZ = moveValue.y;
    }

    void QueueJump()
    {
        if (jumpAction.WasPressedThisFrame() && isGrounded)
            jumpQueued = true;
    }

    // Physics

    void CheckGrounded()
    {
        Vector3 checkOrigin = transform.position;

        bool layerCheck = Physics.CheckSphere(
            checkOrigin,
            groundCheckRadius,
            groundLayer,
            QueryTriggerInteraction.Ignore
        );

        bool fallback = false;
        if (groundLayer.value == 0)
        {
            fallback = Physics.Raycast(
                transform.position,
                Vector3.down,
                groundCheckRadius + 0.1f
            );
        }

        isGrounded = layerCheck || fallback;
    }

    void ApplyMovement()
    {
        Vector3 camForward = cameraTarget != null
            ? Vector3.ProjectOnPlane(cameraTarget.forward, Vector3.up).normalized
            : transform.forward;

        Vector3 camRight = cameraTarget != null
            ? Vector3.ProjectOnPlane(cameraTarget.right, Vector3.up).normalized
            : transform.right;

        Vector3 move = camRight * moveX + camForward * moveZ;

        if (move.magnitude > 1f)
            move.Normalize();

        rb.AddForce(move * moveSpeed, ForceMode.Force);
    }

    void ClampHorizontalSpeed()
    {
        Vector3 flatVelocity = new Vector3(rb.linearVelocity.x, 0f, rb.linearVelocity.z);

        if (flatVelocity.magnitude > maxSpeed)
        {
            Vector3 limited = flatVelocity.normalized * maxSpeed;
            rb.linearVelocity = new Vector3(limited.x, rb.linearVelocity.y, limited.z);
        }
    }

    void ApplyJump()
    {
        if (!jumpQueued) return;

        rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0f, rb.linearVelocity.z);
        rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        jumpQueued = false;
    }

    void OnDrawGizmosSelected()
    {
        Gizmos.color = isGrounded ? Color.green : Color.red;
        Gizmos.DrawWireSphere(transform.position, groundCheckRadius);
    }
}