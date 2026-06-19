using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

public class GameRules : MonoBehaviour
{
    [Header("Panels")]
    public GameObject winPanel;
    public GameObject losePanel;

    [Header("Score")]
    public TMP_Text scoreText;

    [Header("Audio")]
    public AudioClip winSound;
    public AudioClip loseSound;

    [Header("Player")]
    public Transform player;

    private AudioSource audioSource;

    private bool gameEnded = false;

    private float highestY = 0f;

    void Awake()
    {
        if (player == null)
            Debug.LogError("Player missing.");

        if (scoreText == null)
            Debug.LogError("Score Text missing.");

        if (winPanel == null)
            Debug.LogError("Win Panel missing.");

        if (losePanel == null)
            Debug.LogError("Lose Panel missing.");
    }

    void Start()
    {
        audioSource =
            GetComponent<AudioSource>();

        if (player != null)
        {
            highestY = player.position.y;
        }

        if (scoreText != null)
        {
            scoreText.text = "SCORE: 0";
        }

        if (winPanel != null)
            winPanel.SetActive(false);

        if (losePanel != null)
            losePanel.SetActive(false);
    }

    void Update()
    {
        if (gameEnded)
            return;

        if (player == null)
            return;

        if (player.position.y > highestY)
        {
            highestY = player.position.y;

            int score =
                Mathf.RoundToInt(
                    highestY * 10f
                );

            scoreText.text =
                "SCORE: " + score;
        }
    }

    public void PlayerTouchedWater()
    {
        if (gameEnded)
            return;

        gameEnded = true;

        if (loseSound != null)
        {
            audioSource.PlayOneShot(
                loseSound
            );
        }

        DisablePlayer();

        if (losePanel != null)
        {
            losePanel.SetActive(true);
        }

        Time.timeScale = 0f;
    }

    public void PlayerReachedSoapDish()
    {
        if (gameEnded)
            return;

        gameEnded = true;

        if (winSound != null)
        {
            audioSource.PlayOneShot(
                winSound
            );
        }

        DisablePlayer();

        WaterRise water =
            FindFirstObjectByType<WaterRise>();

        if (water != null)
        {
            water.enabled = false;
        }

        if (winPanel != null)
        {
            winPanel.SetActive(true);
        }

        Time.timeScale = 0f;
    }

    void DisablePlayer()
    {
        SoapController controller =
            player.GetComponent<SoapController>();

        if (controller != null)
        {
            controller.enabled = false;
        }

        Rigidbody rb =
            player.GetComponent<Rigidbody>();

        if (rb != null)
        {
            rb.useGravity = false;
            rb.linearVelocity = Vector3.zero;
        }
    }

    public void ReplayGame()
    {
        Time.timeScale = 1f;

        SceneManager.LoadScene(
            "Main_Sink_Level"
        );
    }
}