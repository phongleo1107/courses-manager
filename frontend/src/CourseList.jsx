/* component needs 4 ideas:

1. state for the courses
2. state for loading
3. state for errors
4. `useEffect` fetches onces when the component mounts

*/

import { useEffect, useState } from 'react'

function CourseList() {
  const [courses, setCourses] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadCourses() {
      try {
        const response = await fetch('http://localhost:8000/courses')

        if (!response.ok) {
          throw new Error(`Request failed: ${response.status}`)
        }

        const data = await response.json()
        setCourses(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }

    loadCourses()
  }, [])

  if (isLoading) {
    return <p>Loading courses...</p>
  }

  if (error) {
    return <p role="alert">Could not load courses: {error}</p>
  }

  return (
    <section>
      <h2>Courses</h2>

      {courses.length === 0 ? (
        <p>No courses found.</p>
      ) : (
        <ul>
          {courses.map((course) => (
            <li key={course.id ?? course.name}>
              <strong>{course.name}</strong>
              <span> {course.credits} credits</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default CourseList
