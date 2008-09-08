package sevorg.tic.model;

import java.util.Date;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;

@Entity
public class Activity
{
    /**
     * No-arg constructor for JPA
     */
    public Activity ()
    {}

    /**
     * Creates an activity with the given name that starts now.
     */
    public Activity (String name)
    {
        this.name = name;
        this.start = new Date();
    }

    public void stop ()
    {
        setStop(new Date());
    }

    public long getId ()
    {
        return id;
    }

    public String getName ()
    {
        return name;
    }

    public void setName (String name)
    {
        this.name = name;
    }

    public Date getStart ()
    {
        return start;
    }

    public void setStart (Date start)
    {
        this.start = start;
    }

    public Date getStop ()
    {
        return stop;
    }

    public void setStop (Date stop)
    {
        this.stop = stop;
    }

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private long id;

    private String name;

    private Date start;

    private Date stop;
}
