//the timer(water level)


using UnityEngine;

public class WaterRise : MonoBehaviour
{
    public float riseSpeed = 0.4f;

    public float maxHeight = 50f;

    void Update()
    {
        if (transform.position.y < maxHeight)
        {
            transform.Translate(
                Vector3.up *
                riseSpeed *
                Time.deltaTime,
                Space.World
            );
        }
    }
}