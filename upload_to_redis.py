import os, time, argparse, json
import redis
import json, zlib, base64
from tqdm import tqdm
from dotenv import load_dotenv
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

BATCH_SIZE = 500

def create_index(r: redis.Redis):
    try:
        schema = [
            TextField("$.id", as_name="id"),
            TagField("$.course_dept_tag", as_name="course_dept_tag"), # for filtering
            TextField("$.course_dept", as_name="course_dept", weight=2),
            TextField("$.course_code", as_name="course_code", weight=2),
            TextField("$.class_section", as_name="class_section"),
            TextField("$.course_title", as_name="course_title", weight=2),
            TagField("$.school_tag", as_name="school_tag"), # for filtering
            TextField("$.school", as_name="school"),
            TextField("$.career", as_name="career"),
            TextField("$.class_type", as_name="class_type"),
            TextField("$.credit_hours", as_name="credit_hours"),
            TextField("$.grading_basis", as_name="grading_basis"),
            TextField("$.consent", as_name="consent"),
            NumericField("$.term_year", as_name="term_year"),
            TextField("$.term_season", as_name="term_season"),
            TextField("$.session", as_name="session"),
            TextField("$.dates", as_name="dates"),
            TextField("$.requirements", as_name="requirements"),
            TextField("$.description", as_name="description"),
            TextField("$.notes", as_name="notes"),
            TextField("$.status", as_name="status"),
            NumericField("$.capacity", as_name="capacity"),
            NumericField("$.enrolled", as_name="enrolled"),
            NumericField("$.wl_capacity", as_name="wl_capacity"),
            NumericField("$.wl_occupied", as_name="wl_occupied"),
            TagField("$.attributes", as_name="attributes"),
            TagField("$.meeting_days", as_name="meeting_days"),
            TagField("$.meeting_times", as_name="meeting_times"),
            TagField("$.meeting_dates", as_name="meeting_dates"),
            TextField("$.instructors[*]", as_name="instructors", no_stem=True),
        ]

        r.ft("idx:courses").create_index(
            fields=schema,
            definition=IndexDefinition(prefix=["course:"], index_type=IndexType.JSON)
        )
        print("Index created.")
    except redis.ResponseError as e:
        if "Index already exists" in str(e):
            print("Index already exists, skipping creation.")
        else:
            raise
def upload_courses(r: redis.Redis, courses, dont_skip_unchanged=False):
    pipe = r.pipeline(transaction=False)
    count = 0

    new_courses = 0
    updated_courses = 0
    skipped_courses = 0

    start_time = time.time()
    pbar = tqdm(total=len(courses), desc="Uploading courses", ncols=100, dynamic_ncols=True)

    for course in courses:
        key = f"course:{course['id']}"

        # Only fetch existing data if we need to check for changes
        if dont_skip_unchanged:
            existing = r.json().get(key)
        else:
            # Check if key exists without fetching the data
            existing = r.exists(key)

        if not existing:
            pipe.json().set(key, "$", course, nx=True)
            new_courses += 1
        else:
            if not dont_skip_unchanged:
                # Replace entire document with one command (much more efficient)
                pipe.json().set(key, "$", course)
                updated_courses += 1
            else:
                # Update only changed fields - we have the full existing data
                updated = False
                for field, new_val in course.items():
                    old_val = existing.get(field)
                    if old_val != new_val:
                        pipe.json().set(key, f"$.{field}", new_val)
                        updated = True
                if updated:
                    updated_courses += 1
                else:
                    skipped_courses += 1

        count += 1
        pbar.update(1)

        if count % BATCH_SIZE == 0 or count == len(courses):
            batch_start = time.time()
            pipe.execute()
            batch_end = time.time()
            elapsed = batch_end - start_time
            batch_time = batch_end - batch_start
            pbar.set_postfix(
                {"Total time": f"{elapsed:.1f}s", "Batch time": f"{batch_time:.1f}s"},
                refresh=True,
            )

    pbar.close()

    compressed = base64.b64encode(zlib.compress(json.dumps(courses).encode()))
    r.set("courses:all:compressed", compressed)

    total_elapsed = time.time() - start_time
    print(f"\nAll courses uploaded in {total_elapsed:.1f} seconds")
    print(f"Summary: {new_courses} new, {updated_courses} updated, {skipped_courses} unchanged/skipped")
    print(f"Stored {len(courses)} courses into single key 'courses:all'")

def main():
    parser = argparse.ArgumentParser(description="Upload course data to Redis with optional skip-unchanged")
    parser.add_argument("data_file", help="Path to JSON data file")
    parser.add_argument("--dont-skip-unchanged", action="store_true", help="Don't skip unchanged fields (overwrite all fields)")
    args = parser.parse_args()

    # Load environment variables from .env
    load_dotenv()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    r = redis.Redis.from_url(redis_url)

    # Clear all data from Redis (comment out if you want to update existing data)
    # r.flushall()

    # Load course data
    with open(args.data_file, "r", encoding="utf-8") as f:
        courses = json.load(f)

    # Ensure numeric fields are ints
    for c in courses:
        for field in ["capacity", "enrolled", "wl_capacity", "wl_occupied", "term_year"]:
            if field in c:
                c[field] = int(c[field]) if c[field] is not None else 0
        
        c["course_dept_tag"] = c.get("course_dept", "")
        c["school_tag"] = c.get("school", "")

    create_index(r)
    upload_courses(r, courses, dont_skip_unchanged=not args.dont_skip_unchanged)

if __name__ == "__main__":
    main()
